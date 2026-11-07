from urllib.parse import quote

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from apps.cpns.models import PengaturanCPNS, SkemaUjian, Voucher


class PengaturanCPNSTests(TestCase):
    def test_pengaturan_ambil_satu_baris(self):
        a = PengaturanCPNS.ambil()
        b = PengaturanCPNS.ambil()
        self.assertEqual(a.pk, b.pk)
        self.assertEqual(PengaturanCPNS.objects.count(), 1)

    def test_tautan_wa_kosong_bila_nomor_kosong(self):
        self.assertIsNone(PengaturanCPNS.ambil().tautan_wa(30, "a@b.com"))

    def test_tautan_wa_terisi(self):
        p = PengaturanCPNS.ambil()
        p.nomor_wa = "+62 812-3456"
        tautan = p.tautan_wa(30, "a@b.com")
        self.assertTrue(tautan.startswith("https://wa.me/628123456?text="))
        self.assertIn(quote("Premium 30 hari"), tautan)
        self.assertIn(quote("a@b.com", safe=""), tautan)

    def test_tautan_wa_template_rusak_pakai_bawaan(self):
        p = PengaturanCPNS(nomor_wa="0812345", pesan_wa="Halo {nama} {")
        tautan = p.tautan_wa(30, "a@b.com")
        self.assertTrue(tautan.startswith("https://wa.me/0812345?text="))
        self.assertIn(quote("a@b.com", safe=""), tautan)

    def test_durasi_tersedia_urut(self):
        p = PengaturanCPNS(teks_harga={"90": "x", "30": "y", "abc": "z"})
        self.assertEqual(p.durasi_tersedia(), [30, 90])


class VoucherTests(TestCase):
    def test_status_voucher(self):
        v = Voucher.objects.create(kode="AAAA-BBBB", durasi_hari=30)
        self.assertEqual(v.status, "belum_dipakai")
        user = get_user_model().objects.create_user(
            username="u1", email="u1@x.com", password="x"
        )
        v.dipakai_oleh = user
        v.dipakai_pada = timezone.now()
        self.assertEqual(v.status, "dipakai")
        v.dibatalkan = True
        self.assertEqual(v.status, "dibatalkan")

    def test_kode_voucher_unik(self):
        Voucher.objects.create(kode="AAAA-BBBB", durasi_hari=30)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Voucher.objects.create(kode="AAAA-BBBB", durasi_hari=7)


class UrutanSkemaTests(TestCase):
    def test_skema_skd_lebih_dulu(self):
        kode = list(SkemaUjian.objects.values_list("kode", flat=True))[:2]
        self.assertEqual(kode, ["SKD-CAT", "SKB-GURU-LATIHAN"])
