"""Tes konkurensi dengan thread nyata. Hanya jalan di PostgreSQL.

SQLite tidak menjalankan select_for_update dan mengunci seluruh berkas, jadi
tes ini di-skip di sana dan dijalankan saat rilis.
"""
import threading
from datetime import timedelta
from unittest import skipUnless

from django.contrib.auth import get_user_model
from django.db import close_old_connections, connection
from django.test import Client, SimpleTestCase, TransactionTestCase
from django.urls import resolve, reverse
from django.utils import timezone

from apps.cpns.models import AksesPeserta, PercobaanVoucher, Sesi, SkemaUjian, Voucher
from apps.cpns.tests.pabrik import isi_bank_skd
from apps.cpns.voucher import VoucherDitolak, pakai_voucher


def jalankan_bersamaan(kerja, jumlah=2):
    """Jalankan kerja() di beberapa thread sekaligus. Hasil: daftar (nilai, galat)."""
    gerbang = threading.Barrier(jumlah)
    hasil = [None] * jumlah

    def bungkus(i):
        try:
            gerbang.wait(timeout=10)
            hasil[i] = (kerja(i), None)
        except Exception as e:
            hasil[i] = (None, e)
        finally:
            close_old_connections()
            connection.close()

    threads = [threading.Thread(target=bungkus, args=(i,)) for i in range(jumlah)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
    for t in threads:
        assert not t.is_alive(), "Thread tidak selesai dalam 60 detik."
    return hasil


class AlamatTesKonkurensiTest(SimpleTestCase):
    """Tidak di-skip: memastikan alamat yang dipakai tes Postgres benar-benar ada."""

    def test_alamat_mulai_cat_terpecahkan(self):
        url = reverse("cpns:cat_mulai", args=["SKD-CAT"])
        self.assertEqual(resolve(url).view_name, "cpns:cat_mulai")


@skipUnless(connection.vendor == "postgresql", "Butuh PostgreSQL untuk uji konkurensi.")
class KonkurensiPostgresTest(TransactionTestCase):
    # Menyimpan ulang data migrasi (skema ujian) yang dihapus flush antar tes.
    serialized_rollback = True

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="peserta", email="peserta@contoh.id", password="x"
        )

    def test_dua_thread_satu_voucher_tepat_satu_berhasil(self):
        AksesPeserta.objects.create(user=self.user, via_google=True)
        Voucher.objects.create(kode="AAAA-BBBB", durasi_hari=30)
        sebelum = timezone.now()

        hasil = jalankan_bersamaan(lambda i: pakai_voucher(self.user, "AAAA-BBBB"))

        berhasil = [h for h in hasil if h[1] is None]
        ditolak = [h for h in hasil if isinstance(h[1], VoucherDitolak)]
        self.assertEqual(len(berhasil), 1, hasil)
        self.assertEqual(len(ditolak), 1, hasil)
        akses = AksesPeserta.objects.get(user=self.user)
        self.assertGreaterEqual(akses.premium_sampai, sebelum + timedelta(days=30))
        self.assertLess(akses.premium_sampai, timezone.now() + timedelta(days=31))
        self.assertEqual(Voucher.objects.get(kode="AAAA-BBBB").dipakai_oleh, self.user)
        # Pemenang dan yang kalah sama-sama dicatat atas nama user yang sama.
        percobaan = PercobaanVoucher.objects.filter(user=self.user)
        self.assertEqual(percobaan.filter(berhasil=True).count(), 1)
        self.assertEqual(percobaan.filter(berhasil=False).count(), 1)

    def test_dua_thread_mulai_cat_satu_sesi_berjalan(self):
        AksesPeserta.objects.create(user=self.user, via_google=True)
        isi_bank_skd()
        skema = SkemaUjian.objects.get(kode="SKD-CAT")

        # Klien dan login disiapkan sebelum thread jalan supaya dua POST benar-benar berlomba.
        klien = [Client(), Client()]
        for k in klien:
            k.force_login(self.user)
        url = reverse("cpns:cat_mulai", args=[skema.kode])

        hasil = jalankan_bersamaan(lambda i: klien[i].post(url))

        self.assertTrue(all(h[1] is None for h in hasil), hasil)
        respons = [h[0] for h in hasil]
        self.assertEqual([r.status_code for r in respons], [302, 302])
        sesi = Sesi.objects.get(user=self.user, mode="cat", status="berjalan")
        ruang = reverse("cpns:cat_ruang", args=[sesi.pk])
        dasbor = reverse("cpns:dasbor")
        lokasi = [r["Location"] for r in respons]
        # Pemenang selalu ke ruang. Yang kalah ke ruang yang sama (bentrok di database)
        # atau ke dasbor (terlambat sedikit dan ditolak "selesaikan dulu").
        self.assertIn(ruang, lokasi)
        self.assertTrue(all(l in (ruang, dasbor) for l in lokasi), lokasi)
        self.assertEqual(
            Sesi.objects.filter(user=self.user, mode="cat", status="berjalan").count(), 1
        )

    def test_percobaan_gagal_tetap_tercatat(self):
        with self.assertRaises(VoucherDitolak):
            pakai_voucher(self.user, "ZZZZ-ZZZZ")
        self.assertEqual(
            PercobaanVoucher.objects.filter(user=self.user, berhasil=False).count(), 1
        )
