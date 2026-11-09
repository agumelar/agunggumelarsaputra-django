from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts import batas_masuk
from apps.accounts.models import PercobaanMasuk

User = get_user_model()
SANDI = "SandiKuat-2931"
PESAN = "Terlalu banyak percobaan masuk. Coba lagi dalam 15 menit."


class BatasMasukTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="budi", email="budi@x.id", password=SANDI, role=User.ROLE_PESERTA
        )
        self.url = reverse("cpns:masuk")
        self.kunci = f"u:{self.user.pk}"

    def masuk(self, identitas="budi@x.id", sandi="salah-salah"):
        return self.client.post(
            self.url, {"identitas": identitas, "kata_sandi": sandi}
        )

    def gagal(self, n, identitas="budi@x.id"):
        for _ in range(n):
            self.masuk(identitas)

    def test_lima_gagal_lalu_terkunci(self):
        self.gagal(4)
        self.assertFalse(batas_masuk.terkunci(self.kunci))
        self.gagal(1)
        self.assertTrue(batas_masuk.terkunci(self.kunci))
        self.assertContains(self.masuk(), PESAN, status_code=429)

    def test_variasi_huruf_dan_spasi_dihitung_sama(self):
        for ketikan in ["Budi@x.id", " budi@x.id", "BUDI@X.ID ", "budi@x.id", " Budi@X.id "]:
            self.masuk(ketikan)
        self.assertEqual(PercobaanMasuk.objects.filter(kunci=self.kunci).count(), 5)
        self.assertTrue(batas_masuk.terkunci(self.kunci))

    def test_benar_saat_terkunci_tetap_ditolak(self):
        self.gagal(5)
        r = self.masuk(sandi=SANDI)
        self.assertEqual(r.status_code, 429)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_terbuka_setelah_15_menit(self):
        self.gagal(5)
        nanti = timezone.now() + timedelta(minutes=16)
        with patch("django.utils.timezone.now", return_value=nanti):
            r = self.masuk(sandi=SANDI)
        self.assertEqual(r.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_berhasil_membersihkan(self):
        self.gagal(3)
        self.masuk(sandi=SANDI)
        self.assertEqual(PercobaanMasuk.objects.count(), 0)

    def test_email_dan_username_dihitung_satu_akun(self):
        self.gagal(3, "budi@x.id")
        self.gagal(2, "budi")
        self.assertEqual(self.masuk("budi@x.id", SANDI).status_code, 429)
        self.assertEqual(self.masuk("BUDI", SANDI).status_code, 429)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_berhasil_dengan_username_membersihkan_hitungan_email(self):
        self.gagal(3, "budi@x.id")
        self.masuk("budi", SANDI)
        self.assertEqual(PercobaanMasuk.objects.count(), 0)

    def test_terkunci_tidak_memanggil_authenticate(self):
        self.gagal(5)
        with patch("apps.cpns.views.akun.authenticate") as auth:
            self.masuk(sandi=SANDI)
        auth.assert_not_called()

    def test_identitas_tak_dikenal_tidak_bertabrakan_dengan_kunci_akun(self):
        self.gagal(5, f"u:{self.user.pk}")
        self.assertFalse(batas_masuk.terkunci(self.kunci))

    def test_sekolah_campur_email_username_nisn(self):
        self.user.nisn = "0012345678"
        self.user.save()
        url = reverse("accounts:login")
        for ketik in ["budi@x.id", "budi", "0012345678", "BUDI@x.id", "Budi"]:
            self.client.post(url, {"identifier": ketik, "password": "salah-salah"})
        r = self.client.post(url, {"identifier": "0012345678", "password": SANDI})
        self.assertContains(r, PESAN, status_code=429)

    def test_login_sekolah_juga_dibatasi(self):
        url = reverse("accounts:login")
        for _ in range(5):
            self.client.post(url, {"identifier": "Budi@x.id", "password": "salah-salah"})
        r = self.client.post(url, {"identifier": " budi@x.id", "password": SANDI})
        self.assertContains(r, PESAN, status_code=429)
        self.assertContains(r, 'role="alert"', status_code=429)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_status_429(self):
        self.gagal(5)
        r = self.masuk()
        self.assertEqual(r.status_code, 429)
        self.assertContains(r, 'role="alert"', status_code=429)

    def test_akun_google_tidak_dihitung(self):
        User.objects.create_user(username="gia", email="gia@x.id", role=User.ROLE_PESERTA)
        self.gagal(6, "gia@x.id")
        self.assertEqual(PercobaanMasuk.objects.count(), 0)

    def test_baris_lebih_dari_sehari_dihapus(self):
        lama = timezone.now() - timedelta(days=2)
        PercobaanMasuk.objects.create(kunci="lama", waktu=lama)
        batas_masuk.catat_gagal("i:baru")
        self.assertFalse(PercobaanMasuk.objects.filter(kunci="lama").exists())
