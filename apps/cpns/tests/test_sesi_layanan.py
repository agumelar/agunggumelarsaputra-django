from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.cpns.models import SkemaUjian
from apps.cpns.sesi_layanan import (
    SesiSudahSelesai,
    WaktuHabis,
    kumpulkan,
    selesaikan_jika_kedaluwarsa,
    simpan_jawaban,
)
from apps.cpns.tests.pabrik import buat_sesi_cat, buat_soal


class SesiLayananTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="p", password="x")
        self.skema = SkemaUjian.objects.get(kode="SKD-CAT")
        self.soal = [buat_soal("TWK", kunci="A") for _ in range(3)]
        self.sesi = buat_sesi_cat(self.user, self.skema, self.soal, ["", "", ""])
        self.batas = timezone.now() + timedelta(minutes=10)
        self.sesi.batas_waktu = self.batas
        self.sesi.save(update_fields=["batas_waktu"])

    def test_simpan_menerjemahkan_posisi_ke_asli(self):
        butir = self.sesi.butir.get(nomor=1)
        butir.urutan_opsi = "CAEBD"
        butir.save(update_fields=["urutan_opsi"])
        hasil = simpan_jawaban(self.sesi, 1, "A", False)
        self.assertEqual(hasil.jawaban, "C")
        butir.refresh_from_db()
        self.assertEqual(butir.jawaban, "C")

    def test_simpan_idempoten(self):
        simpan_jawaban(self.sesi, 2, "B", True)
        simpan_jawaban(self.sesi, 2, "B", True)
        qs = self.sesi.butir.filter(nomor=2)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.get().jawaban, "B")
        self.assertTrue(qs.get().ragu)

    def test_simpan_ditolak_setelah_toleransi(self):
        with self.assertRaises(WaktuHabis):
            simpan_jawaban(self.sesi, 1, "A", False, now=self.batas + timedelta(seconds=31))
        hasil = simpan_jawaban(self.sesi, 1, "A", False, now=self.batas + timedelta(seconds=29))
        self.assertEqual(hasil.jawaban, "A")

    def test_jawaban_tidak_valid_ditolak(self):
        with self.assertRaises(ValueError):
            simpan_jawaban(self.sesi, 1, "F", False)
        with self.assertRaises(ValueError):
            simpan_jawaban(self.sesi, 999, "A", False)

    def test_simpan_ditolak_kalau_sesi_selesai(self):
        kumpulkan(self.sesi)
        self.sesi.refresh_from_db()
        with self.assertRaises(SesiSudahSelesai):
            simpan_jawaban(self.sesi, 1, "A", False)

    def test_simpan_ditolak_pada_objek_basi_yang_sudah_dikumpulkan(self):
        basi = type(self.sesi).objects.get(pk=self.sesi.pk)
        simpan_jawaban(self.sesi, 1, "A", False)
        kumpulkan(self.sesi)
        self.assertEqual(basi.status, "berjalan")
        with self.assertRaises(SesiSudahSelesai):
            simpan_jawaban(basi, 1, "B", False)
        self.assertEqual(self.sesi.butir.get(nomor=1).jawaban, "A")

    def test_kosongkan_jawaban(self):
        simpan_jawaban(self.sesi, 1, "A", False)
        hasil = simpan_jawaban(self.sesi, 1, "", False)
        self.assertEqual(hasil.jawaban, "")

    def test_kumpulkan_dua_kali_hasil_sama(self):
        simpan_jawaban(self.sesi, 1, "A", False)
        pertama = kumpulkan(self.sesi, now=timezone.now())
        total, selesai = pertama.total, pertama.selesai_pada
        kedua = kumpulkan(self.sesi, now=timezone.now() + timedelta(minutes=5))
        self.assertEqual(kedua.status, "selesai")
        self.assertEqual(kedua.total, total)
        self.assertEqual(kedua.selesai_pada, selesai)

    def test_soal_ditolak_setelah_sesi_dibuat_tetap_dinilai(self):
        simpan_jawaban(self.sesi, 1, "A", False)
        self.soal[0].status = "ditolak"
        self.soal[0].save(update_fields=["status"])
        hasil = kumpulkan(self.sesi)
        self.assertGreater(hasil.total, 0)

    def test_kedaluwarsa_otomatis_dikumpulkan(self):
        simpan_jawaban(self.sesi, 1, "A", False)
        self.assertFalse(
            selesaikan_jika_kedaluwarsa(self.sesi, now=self.batas + timedelta(seconds=10))
        )
        self.sesi.refresh_from_db()
        self.assertEqual(self.sesi.status, "berjalan")
        self.assertTrue(
            selesaikan_jika_kedaluwarsa(self.sesi, now=self.batas + timedelta(seconds=31))
        )
        self.sesi.refresh_from_db()
        self.assertEqual(self.sesi.status, "selesai")
        self.assertFalse(
            selesaikan_jika_kedaluwarsa(self.sesi, now=self.batas + timedelta(seconds=60))
        )
