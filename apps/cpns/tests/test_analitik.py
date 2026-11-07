from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.test import TestCase

from apps.cpns.analitik import kelemahan_subtopik
from apps.cpns.models import Sesi, SesiSoal, SkemaUjian
from apps.cpns.tests.pabrik import buat_sesi_cat, buat_soal


def _belajar(user, subtes, subtopik, jawaban_list):
    """Sesi belajar dengan soal berkunci A; jawaban 'A' benar, 'B' salah, '' belum dijawab."""
    sesi = Sesi.objects.create(user=user, mode="belajar")
    for nomor, jawaban in enumerate(jawaban_list, start=1):
        SesiSoal.objects.create(
            sesi=sesi,
            soal=buat_soal(subtes, subtopik=subtopik, kunci="A"),
            nomor=nomor,
            urutan_opsi="ABCDE",
            jawaban=jawaban,
        )
    return sesi


class KelemahanSubtopikTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("lemah", email="lemah@contoh.id", password="x")

    def test_kelemahan_urut_dan_ambang_minimal(self):
        _belajar(self.user, "TIU", "Silogisme", ["A", "A", "B", "B", "B"])  # 2/5 = 40%
        _belajar(self.user, "TWK", "Pancasila", ["A", "B", "B"])  # 1/3 = 33%
        _belajar(self.user, "TIU", "Deret", ["A", "A", "A", "B"])  # 3/4 = 75%
        _belajar(self.user, "TWK", "Pelayanan", ["B", "B"])  # 0/2, di bawah ambang
        _belajar(self.user, "TWK", "Nasionalisme", ["A", "B", "", ""])  # 1/2 dijawab, di bawah ambang
        hasil = kelemahan_subtopik(self.user)
        self.assertEqual(
            [(h["subtes"], h["subtopik"]) for h in hasil],
            [("TWK", "Pancasila"), ("TIU", "Silogisme"), ("TIU", "Deret")],
        )
        self.assertEqual(hasil[1]["benar"], 2)
        self.assertEqual(hasil[1]["dijawab"], 5)
        self.assertEqual(hasil[1]["persen"], 40)

    def test_kelemahan_seri_dijawab_terbanyak_dan_batas(self):
        _belajar(self.user, "TIU", "A-sedikit", ["A", "B", "B"])  # 1/3
        _belajar(self.user, "TWK", "B-banyak", ["A", "B", "B", "B", "A", "B"])  # 2/6 = 33
        _belajar(self.user, "TWK", "C", ["A", "A", "B", "B", "A", "A"])  # 4/6
        hasil = kelemahan_subtopik(self.user, batas=2)
        self.assertEqual(len(hasil), 2)
        self.assertEqual(hasil[0]["subtopik"], "B-banyak")
        self.assertEqual(hasil[1]["subtopik"], "A-sedikit")

    def test_kelemahan_gabung_beberapa_sesi_dan_milik_sendiri(self):
        _belajar(self.user, "TIU", "Silogisme", ["B", "B"])
        _belajar(self.user, "TIU", "Silogisme", ["A", "B"])
        lain = get_user_model().objects.create_user("lain", email="lain@contoh.id", password="x")
        _belajar(lain, "TIU", "Silogisme", ["A", "A", "A", "A"])
        hasil = kelemahan_subtopik(self.user)
        self.assertEqual(len(hasil), 1)
        self.assertEqual((hasil[0]["benar"], hasil[0]["dijawab"]), (1, 4))

    def test_kelemahan_abaikan_cat(self):
        skema = SkemaUjian.objects.get(kode="SKD-CAT")
        soal = [buat_soal("TIU", subtopik="Silogisme") for _ in range(5)]
        buat_sesi_cat(self.user, skema, soal, ["B"] * 5)
        self.assertEqual(kelemahan_subtopik(self.user), [])


class BarSkorTest(TestCase):
    def _render(self, skor, maks, ambang):
        return Template(
            "{% include 'cpns/komponen/bar_skor.html' with subtes='TIU' skor=skor maks=maks ambang=ambang lulus=True %}"
        ).render(Context({"skor": skor, "maks": maks, "ambang": ambang}))

    def test_bar_skor_dibatasi_100(self):
        html = self._render(200, 150, 300)
        self.assertIn("width: 100%", html)
        self.assertIn("left: 100%", html)
        self.assertNotIn("133%", html)
        self.assertNotIn("200%", html)

    def test_bar_skor_normal_dan_negatif(self):
        self.assertIn("width: 50%", self._render(75, 150, 100))
        self.assertIn("width: 0%", self._render(-10, 150, 100))
