from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.cpns.models import Sesi, SesiSoal, SkemaBagian, SkemaUjian
from apps.cpns.penilaian import adalah_benar, bagian_implisit, nilai_sesi, poin_soal
from apps.cpns.tests.pabrik import buat_sesi_cat, buat_soal


class PenilaianTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="p", password="x")
        self.skema = SkemaUjian.objects.get(kode="SKD-CAT")

    def _sesi(self, twk, tiu, tkp):
        """Tiap argumen: daftar jawaban untuk subtes itu."""
        soal, jawaban = [], []
        for subtes, daftar in (("TWK", twk), ("TIU", tiu), ("TKP", tkp)):
            for j in daftar:
                soal.append(buat_soal(subtes, kunci="A"))
                jawaban.append(j)
        return buat_sesi_cat(self.user, self.skema, soal, jawaban)

    def test_twk_benar_5_salah_0_kosong_0(self):
        s = buat_soal("TWK", kunci="B")
        bagian = self.skema.bagian.get(subtes="TWK")
        self.assertEqual(poin_soal(s, "B", bagian), 5)
        self.assertEqual(poin_soal(s, "C", bagian), 0)
        self.assertEqual(poin_soal(s, "", bagian), 0)

    def test_tkp_pakai_bobot_dan_kosong_0(self):
        s = buat_soal("TKP")
        bagian = self.skema.bagian.get(subtes="TKP")
        self.assertEqual(poin_soal(s, "A", bagian), 1)
        self.assertEqual(poin_soal(s, "E", bagian), 5)
        self.assertEqual(poin_soal(s, "", bagian), 0)

    def test_bobot_opsi_jawaban_tak_dikenal_0(self):
        s = buat_soal("TKP", bobot={"A": 5})
        bagian = self.skema.bagian.get(subtes="TKP")
        self.assertEqual(poin_soal(s, "B", bagian), 0)

    def test_lulus_jika_semua_bagian_capai_ambang(self):
        # 13 benar TWK = 65, 16 benar TIU = 80, 34 x E (5) + 1 x A(1)... = 166
        sesi = self._sesi(["A"] * 13, ["A"] * 16, ["E"] * 33 + ["A"])
        nilai_sesi(sesi)
        sesi.refresh_from_db()
        self.assertEqual([b["skor"] for b in sesi.skor_bagian], [65, 80, 166])
        self.assertTrue(sesi.lulus)

    def test_gagal_jika_satu_bagian_kurang(self):
        sesi = self._sesi(["A"] * 13, ["A"] * 15, ["E"] * 33 + ["A"])
        nilai_sesi(sesi)
        sesi.refresh_from_db()
        self.assertEqual(sesi.skor_bagian[1]["skor"], 75)
        self.assertFalse(sesi.lulus)
        self.assertIs(sesi.skor_bagian[1]["lulus"], False)

    def test_total_jumlah_semua_bagian(self):
        # 70 + 75 + 170
        sesi = self._sesi(["A"] * 14, ["A"] * 15, ["E"] * 34)
        nilai_sesi(sesi)
        sesi.refresh_from_db()
        self.assertEqual(sesi.total, 315)
        self.assertEqual(
            sesi.skor_bagian[0],
            {"subtes": "TWK", "skor": 70, "maks": 150, "ambang": 65, "lulus": True},
        )
        self.assertEqual(sesi.skor_bagian[2]["maks"], 225)

    def test_butir_poin_terisi_dan_status_tak_berubah(self):
        sesi = self._sesi(["A", "B", ""], [], [])
        nilai_sesi(sesi)
        self.assertEqual(
            list(SesiSoal.objects.filter(sesi=sesi).values_list("poin", flat=True)),
            [5, 0, 0],
        )
        self.assertEqual(Sesi.objects.get(pk=sesi.pk).status, "berjalan")

    def test_sesi_belajar_dinilai_per_subtes(self):
        sesi = Sesi.objects.create(user=self.user, mode="belajar")
        data = [
            (buat_soal("TIU", kunci="A"), "A"),
            (buat_soal("TKP"), "C"),
            (buat_soal("TIU", kunci="A"), "B"),
        ]
        for n, (s, j) in enumerate(data, start=1):
            SesiSoal.objects.create(
                sesi=sesi, soal=s, nomor=n, urutan_opsi="ABCDE", jawaban=j
            )
        nilai_sesi(sesi)
        sesi.refresh_from_db()
        self.assertEqual(
            sesi.skor_bagian,
            [
                {"subtes": "TIU", "skor": 5, "maks": 10, "ambang": 0, "lulus": True},
                {"subtes": "TKP", "skor": 3, "maks": 5, "ambang": 0, "lulus": True},
            ],
        )
        self.assertEqual(sesi.total, 8)
        self.assertTrue(sesi.lulus)

    def test_bagian_implisit_tidak_disimpan(self):
        b = bagian_implisit(buat_soal("TKP"))
        self.assertIsInstance(b, SkemaBagian)
        self.assertEqual(b.cara_nilai, "bobot_opsi")
        self.assertIsNone(b.pk)

    def test_adalah_benar(self):
        tiu = buat_soal("TIU", kunci="C")
        self.assertTrue(adalah_benar(tiu, "C"))
        self.assertFalse(adalah_benar(tiu, "D"))
        self.assertFalse(adalah_benar(tiu, ""))
        tkp = buat_soal("TKP")
        self.assertTrue(adalah_benar(tkp, "E"))
        self.assertFalse(adalah_benar(tkp, "D"))
        self.assertFalse(adalah_benar(tkp, ""))
