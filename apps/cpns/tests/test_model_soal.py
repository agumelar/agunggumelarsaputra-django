from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.cpns.models import LaporanSoal
from apps.cpns.tests.pabrik import buat_soal
from apps.cpns.tests.test_dasbor import buat_user
from apps.cpns.validasi import sidik_teks


class SoalSidikTest(TestCase):
    def test_update_fields_teks_ikut_sidik(self):
        s = buat_soal("TIU")
        s.teks = "baru"
        s.save(update_fields=["teks"])
        s.refresh_from_db()
        self.assertEqual(s.sidik_teks, sidik_teks("baru"))

    def test_hitung_sidik_publik(self):
        s = buat_soal("TIU", teks="Halo, dunia!")
        self.assertEqual(s.hitung_sidik(), sidik_teks("Halo, dunia!"))


class LaporanGandaTest(TestCase):
    def test_laporan_baru_ganda_ditolak_db(self):
        soal = buat_soal("TIU")
        user = buat_user("pelapor")
        pertama = LaporanSoal.objects.create(soal=soal, user=user, alasan="typo")
        with self.assertRaises(IntegrityError), transaction.atomic():
            LaporanSoal.objects.create(soal=soal, user=user, alasan="typo")
        LaporanSoal.objects.filter(pk=pertama.pk).update(status="selesai")
        LaporanSoal.objects.create(soal=soal, user=user, alasan="typo")
        self.assertEqual(LaporanSoal.objects.count(), 2)
