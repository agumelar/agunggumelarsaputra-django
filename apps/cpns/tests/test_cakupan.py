from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.cpns.cakupan import hitung_cakupan
from apps.cpns.kisi_kisi import Subtopik
from apps.cpns.models import SkemaBagian, SkemaUjian
from apps.cpns.tests.pabrik import buat_soal

KISI = [
    Subtopik("SKD", "TIU", "Deret", 5),
    Subtopik("SKD", "TWK", "Pancasila", 3),
]


def _kisi(testcase, daftar=KISI):
    from unittest import mock

    pesan = mock.patch("apps.cpns.cakupan.baca_kisi_kisi", return_value=daftar)
    pesan.start()
    testcase.addCleanup(pesan.stop)


class HitungCakupanTest(TestCase):
    def setUp(self):
        _kisi(self)

    def test_cakupan_bank_kosong(self):
        hasil = hitung_cakupan()
        by = {(b["subtes"], b["subtopik"]): b for b in hasil["baris"]}
        deret = by[("TIU", "Deret")]
        self.assertEqual((deret["target"], deret["tayang"], deret["draf"], deret["kurang"]), (5, 0, 0, 5))
        self.assertTrue(hasil["skema"])
        for skema in hasil["skema"]:
            if skema["kode"] == "SKD-CAT":
                self.assertEqual(skema["cukup_untuk"], 0)

    def test_hitung_tayang_draf_dan_kurang(self):
        for _ in range(2):
            buat_soal("TIU", subtopik="Deret")
        buat_soal("TIU", subtopik="Deret", status="draf")
        buat_soal("TIU", subtopik="Deret", status="ditolak")
        for _ in range(7):
            buat_soal("TWK", subtopik="Pancasila")
        by = {(b["subtes"], b["subtopik"]): b for b in hitung_cakupan()["baris"]}
        self.assertEqual((by[("TIU", "Deret")]["tayang"], by[("TIU", "Deret")]["draf"], by[("TIU", "Deret")]["kurang"]), (2, 1, 3))
        self.assertEqual(by[("TWK", "Pancasila")]["kurang"], 0)

    def test_cukup_untuk_minimum_bagian(self):
        skema = SkemaUjian.objects.create(kode="UJI", nama="Uji", jenis_ujian="SKD", durasi_menit=10)
        SkemaBagian.objects.create(skema=skema, urutan=1, subtes="TWK", jumlah_soal=2, cara_nilai="benar_salah")
        SkemaBagian.objects.create(skema=skema, urutan=2, subtes="TIU", jumlah_soal=3, cara_nilai="benar_salah")
        for _ in range(10):
            buat_soal("TWK")
        for _ in range(7):
            buat_soal("TIU")
        buat_soal("TIU", status="draf")
        by = {s["kode"]: s for s in hitung_cakupan()["skema"]}
        self.assertEqual(by["UJI"]["cukup_untuk"], 2)  # min(10//2, 7//3)

    def test_jumlah_soal_nol_tidak_error(self):
        skema = SkemaUjian.objects.create(kode="NOL", nama="Nol", jenis_ujian="SKD", durasi_menit=10)
        SkemaBagian.objects.create(skema=skema, urutan=1, subtes="TWK", jumlah_soal=0, cara_nilai="benar_salah")
        SkemaUjian.objects.create(kode="TANPA", nama="Tanpa", jenis_ujian="SKD", durasi_menit=10)
        by = {s["kode"]: s for s in hitung_cakupan()["skema"]}
        self.assertEqual(by["NOL"]["cukup_untuk"], 0)
        self.assertEqual(by["TANPA"]["cukup_untuk"], 0)

    def test_subtopik_di_luar_kisi_kisi_tampil_tanpa_target(self):
        buat_soal("TIU", subtopik="Topik Liar")
        buat_soal("TIU", subtopik="Topik Liar", status="draf")
        by = {(b["subtes"], b["subtopik"]): b for b in hitung_cakupan()["baris"]}
        liar = by[("TIU", "Topik Liar")]
        self.assertIsNone(liar["target"])
        self.assertEqual((liar["tayang"], liar["draf"], liar["kurang"]), (1, 1, 0))


class HalamanCakupanTest(TestCase):
    def setUp(self):
        _kisi(self)
        self.admin = get_user_model().objects.create_superuser(
            username="agung", email="a@contoh.id", password="x"
        )

    def test_halaman_cakupan_superuser_saja(self):
        url = reverse("cpns:kelola_cakupan")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r["Location"].startswith(reverse("cpns:masuk")))
        self.client.force_login(get_user_model().objects.create_user(username="guru", password="x"))
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_halaman_isi(self):
        self.client.force_login(self.admin)
        buat_soal("TIU", subtopik="Deret")
        buat_soal("TWK", subtopik="Pancasila")
        for _ in range(3):
            buat_soal("TWK", subtopik="Pancasila")
        r = self.client.get(reverse("cpns:kelola_cakupan"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Kurang 4")
        self.assertContains(r, "Cukup")
        self.assertContains(r, "tanpa soal berulang")
        self.assertContains(r, "subtopik=Deret")

    def test_kisi_kisi_rusak_tetap_tampil_dengan_pesan(self):
        from unittest import mock

        self.client.force_login(self.admin)
        buat_soal("TIU", subtopik="Deret")
        rusak = mock.patch(
            "apps.cpns.cakupan.baca_kisi_kisi",
            side_effect=ValueError("Kisi-kisi baris 9: target abc harus angka positif."),
        )
        with rusak:
            r = self.client.get(reverse("cpns:kelola_cakupan"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(
            r, "Kisi-kisi tidak bisa dibaca: Kisi-kisi baris 9: target abc harus angka positif."
        )
        self.assertContains(r, "subtopik=Deret")

    def test_tinjau_menaut_ke_cakupan(self):
        self.client.force_login(self.admin)
        r = self.client.get(reverse("cpns:kelola_tinjau"))
        self.assertContains(r, reverse("cpns:kelola_cakupan"))
