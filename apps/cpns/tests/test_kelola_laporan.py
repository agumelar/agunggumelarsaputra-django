from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.cpns.models import LaporanSoal
from apps.cpns.tests.pabrik import buat_soal


class LaporanBase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_superuser(username="agung", email="a@contoh.id", password="x")
        self.p1 = User.objects.create_user(
            username="budi01", email="budi@rahasia.id", password="x", first_name="Budi"
        )
        self.p2 = User.objects.create_user(username="sari02", email="sari@rahasia.id", password="x")
        self.client.force_login(self.admin)
        self.url = reverse("cpns:kelola_laporan")


class LaporanTest(LaporanBase):
    def test_tinjau_menaut_ke_cakupan_dan_laporan(self):
        r = self.client.get(reverse("cpns:kelola_tinjau"))
        self.assertContains(r, reverse("cpns:kelola_cakupan"))
        self.assertContains(r, reverse("cpns:kelola_laporan"))

    def test_daftar_laporan_baru(self):
        soal = buat_soal("TIU", teks="Berapa hasil dua tambah dua?")
        LaporanSoal.objects.create(soal=soal, user=self.p1, alasan="kunci_salah", catatan="Kuncinya keliru")
        LaporanSoal.objects.create(soal=soal, user=self.p2, alasan="typo", status="selesai")
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Kunci salah")
        self.assertContains(r, "Kuncinya keliru")
        self.assertContains(r, "Berapa hasil dua tambah dua?")
        self.assertContains(r, "Budi")
        self.assertContains(r, reverse("cpns:kelola_tinjau_soal", args=[soal.id]))
        self.assertContains(r, "Tinjau soal ini")
        self.assertContains(r, "Tandai selesai")
        self.assertNotContains(r, "Salah ketik")

    def test_keadaan_kosong(self):
        self.assertContains(self.client.get(self.url), "Belum ada laporan baru.")

    def test_tanpa_email_pelapor(self):
        soal = buat_soal("TIU")
        LaporanSoal.objects.create(soal=soal, user=self.p1, alasan="typo")
        LaporanSoal.objects.create(soal=soal, user=self.p2, alasan="ambigu")
        r = self.client.get(self.url)
        self.assertContains(r, "sari02")
        self.assertNotContains(r, "rahasia.id")

    def test_tandai_selesai(self):
        soal = buat_soal("TIU")
        lap = LaporanSoal.objects.create(soal=soal, user=self.p1, alasan="typo")
        url = reverse("cpns:kelola_laporan_selesai", args=[lap.id])
        r = self.client.post(url, {"status": "baru"})
        self.assertRedirects(r, self.url, fetch_redirect_response=False)
        lap.refresh_from_db()
        self.assertEqual(lap.status, "selesai")
        self.assertEqual(self.client.get(url).status_code, 405)

    def test_tandai_selesai_balik_ke_filter_sama(self):
        soal = buat_soal("TIU")
        lap = LaporanSoal.objects.create(soal=soal, user=self.p1, alasan="typo")
        r = self.client.post(reverse("cpns:kelola_laporan_selesai", args=[lap.id]), {"status": "semua"})
        self.assertEqual(r["Location"], f"{self.url}?status=semua")

    def test_kelompok_per_soal(self):
        a = buat_soal("TIU", teks="Soal kelompok A")
        b = buat_soal("TWK", teks="Soal kelompok B")
        LaporanSoal.objects.create(soal=a, user=self.p1, alasan="typo")
        LaporanSoal.objects.create(soal=a, user=self.p2, alasan="ambigu")
        LaporanSoal.objects.create(soal=b, user=self.p1, alasan="typo")
        r = self.client.get(self.url)
        self.assertEqual(len(r.context["kelompok"]), 2)
        jumlah = {k["soal"].id: k["jumlah"] for k in r.context["kelompok"]}
        self.assertEqual(jumlah, {a.id: 2, b.id: 1})
        self.assertContains(r, "2 laporan")
        self.assertContains(r, "Soal kelompok A", count=1)

    def test_tanpa_n_plus_satu(self):
        for i in range(4):
            LaporanSoal.objects.create(
                soal=buat_soal("TIU"), user=self.p1 if i % 2 else self.p2, alasan="typo"
            )
        with self.assertNumQueries(4):
            self.client.get(self.url)

    def test_nav_menampilkan_jumlah(self):
        soal = buat_soal("TIU")
        LaporanSoal.objects.create(soal=soal, user=self.p1, alasan="typo")
        LaporanSoal.objects.create(soal=soal, user=self.p2, alasan="typo")
        self.assertContains(self.client.get(self.url), "Laporan Soal (2)")


class AksesLaporanTest(LaporanBase):
    def test_akses_superuser_saja(self):
        soal = buat_soal("TIU")
        lap = LaporanSoal.objects.create(soal=soal, user=self.p1, alasan="typo")
        selesai = reverse("cpns:kelola_laporan_selesai", args=[lap.id])
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)
        r = self.client.post(selesai)
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r["Location"].startswith(reverse("cpns:masuk")))
        self.client.force_login(self.p2)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertEqual(self.client.post(selesai).status_code, 403)
        lap.refresh_from_db()
        self.assertEqual(lap.status, "baru")
