from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.cpns.models import PaketBelajar, SkemaUjian


class SkemaAwalTests(TestCase):
    def test_skema_skd_terpasang(self):
        skema = SkemaUjian.objects.get(kode="SKD-CAT")
        self.assertEqual(skema.durasi_menit, 100)
        bagian = [
            (b.subtes, b.jumlah_soal, b.cara_nilai, b.ambang_batas)
            for b in skema.bagian.all()
        ]
        self.assertEqual(
            bagian,
            [
                ("TWK", 30, "benar_salah", 65),
                ("TIU", 35, "benar_salah", 80),
                ("TKP", 45, "bobot_opsi", 166),
            ],
        )
        self.assertEqual(skema.total_soal, 110)

    def test_skema_skb_nonaktif(self):
        skema = SkemaUjian.objects.get(kode="SKB-GURU-LATIHAN")
        self.assertFalse(skema.aktif)
        self.assertEqual(skema.durasi_menit, 90)
        bagian = [(b.subtes, b.jumlah_soal, b.ambang_batas) for b in skema.bagian.all()]
        self.assertEqual(bagian, [("PEDAGOGIK", 50, 0), ("MATERI_RPL", 50, 0)])


class PaketTrialTests(TestCase):
    def test_hanya_satu_paket_trial_aktif(self):
        PaketBelajar.objects.create(nama="A", jenis_ujian="SKD", untuk_trial=True)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PaketBelajar.objects.create(nama="B", jenis_ujian="SKD", untuk_trial=True)
        PaketBelajar.objects.create(nama="C", jenis_ujian="SKD", untuk_trial=True, aktif=False)
        PaketBelajar.objects.create(nama="D", jenis_ujian="SKB_GURU", untuk_trial=True)
