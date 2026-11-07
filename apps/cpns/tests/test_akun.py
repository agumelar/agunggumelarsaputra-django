from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.cpns.models import AksesPeserta, PengaturanCPNS
from apps.gamification.models import XPHistory

User = get_user_model()
HOST_CPNS = "cpns.agunggumelarsaputra.com"
SANDI = "SandiKuat-2931"


def data_daftar(**ganti):
    data = {
        "nama": "Sari Dewi",
        "email": "sari@contoh.id",
        "kata_sandi": SANDI,
        "ulang_kata_sandi": SANDI,
        "setuju": "on",
    }
    data.update(ganti)
    return data


class DaftarTest(TestCase):
    def daftar(self, **ganti):
        return self.client.post(reverse("cpns:daftar"), data_daftar(**ganti))

    def test_halaman_daftar_tampil(self):
        r = self.client.get(reverse("cpns:daftar"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Saya setuju dengan")

    def test_daftar_membuat_peserta(self):
        r = self.daftar()
        self.assertRedirects(r, reverse("cpns:dasbor"), fetch_redirect_response=False)
        user = User.objects.get(email="sari@contoh.id")
        self.assertEqual(user.role, "peserta")
        self.assertEqual(user.username, "sari")
        self.assertEqual(user.first_name, "Sari Dewi")
        self.assertEqual(user.xp, 0)
        self.assertFalse(XPHistory.objects.filter(user=user).exists())
        self.assertFalse(AksesPeserta.objects.get(user=user).via_google)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_daftar_username_dibuat_unik(self):
        User.objects.create_user(username="sari", email="lain@contoh.id", password="x")
        self.daftar()
        self.assertEqual(User.objects.get(email="sari@contoh.id").username, "sari1")

    def test_daftar_email_siswa_ditolak(self):
        siswa = User.objects.create_user(
            username="siswa1", email="Sari@Contoh.id", password="x", role="siswa"
        )
        r = self.daftar()
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Email ini sudah terdaftar. Silakan masuk.")
        siswa.refresh_from_db()
        self.assertEqual(siswa.role, "siswa")
        self.assertEqual(User.objects.count(), 1)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_daftar_tanpa_setuju_ditolak(self):
        data = data_daftar()
        del data["setuju"]
        r = self.client.post(reverse("cpns:daftar"), data)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(email="sari@contoh.id").exists())

    def test_daftar_sandi_tidak_sama_ditolak(self):
        r = self.daftar(ulang_kata_sandi="BedaSandi-1234")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Kata sandi dan ulangannya tidak sama.")
        self.assertFalse(User.objects.filter(email="sari@contoh.id").exists())

    def test_daftar_sandi_lemah_ditolak(self):
        r = self.daftar(kata_sandi="12345678", ulang_kata_sandi="12345678")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(email="sari@contoh.id").exists())

    def test_daftar_sudah_login_ke_dasbor(self):
        self.daftar()
        r = self.client.get(reverse("cpns:daftar"))
        self.assertRedirects(r, reverse("cpns:dasbor"), fetch_redirect_response=False)


class MasukTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="budi", email="budi@contoh.id", password=SANDI, role="peserta"
        )

    def masuk(self, identitas, sandi=SANDI, url=None):
        return self.client.post(
            url or reverse("cpns:masuk"),
            {"identitas": identitas, "kata_sandi": sandi},
        )

    def test_halaman_masuk_memuat_teks_wajib(self):
        PengaturanCPNS.objects.update_or_create(pk=1, defaults={"nomor_wa": "+62 812-3456"})
        r = self.client.get(reverse("cpns:masuk"))
        self.assertContains(r, "Masuk dengan Google")
        self.assertContains(r, reverse("accounts:google_login"))
        self.assertContains(r, "Simulasi CAT gratis hanya tersedia untuk akun Google.")
        self.assertContains(r, "Lupa kata sandi? Hubungi admin lewat WhatsApp untuk mengatur ulang.")
        self.assertContains(r, "https://wa.me/628123456")

    def test_tanpa_nomor_wa_tidak_ada_tautan(self):
        r = self.client.get(reverse("cpns:masuk"))
        self.assertNotContains(r, "wa.me")

    def test_masuk_dengan_email_dan_username(self):
        for identitas in ("budi@contoh.id", "BUDI@contoh.id", "budi"):
            self.client.logout()
            r = self.masuk(identitas)
            self.assertRedirects(r, reverse("cpns:dasbor"), fetch_redirect_response=False)
            self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_masuk_gagal(self):
        r = self.masuk("budi", "salah-sekali")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Email atau kata sandi salah.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_masuk_next_internal_diikuti(self):
        url = reverse("cpns:masuk") + "?next=" + reverse("cpns:riwayat")
        r = self.masuk("budi", url=url)
        self.assertRedirects(r, reverse("cpns:riwayat"), fetch_redirect_response=False)

    def test_masuk_next_eksternal_diabaikan(self):
        url = reverse("cpns:masuk") + "?next=https://evil.example.com/"
        r = self.masuk("budi", url=url)
        self.assertRedirects(r, reverse("cpns:dasbor"), fetch_redirect_response=False)

    def test_sudah_login_diarahkan_ke_dasbor(self):
        self.client.force_login(self.user)
        r = self.client.get(reverse("cpns:masuk"))
        self.assertRedirects(r, reverse("cpns:dasbor"), fetch_redirect_response=False)

    def test_tamu_ke_dasbor_diarahkan_ke_masuk_cpns(self):
        r = self.client.get(reverse("cpns:dasbor"))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r["Location"].startswith(reverse("cpns:masuk")))

    def test_header_tamu_masuk_dan_user_keluar(self):
        r = self.client.get(reverse("cpns:masuk"))
        self.assertContains(r, ">Masuk<")
        self.client.force_login(self.user)
        r = self.client.get(reverse("cpns:dasbor"))
        self.assertContains(r, reverse("accounts:logout"))
        self.assertContains(r, ">Keluar<")


def respons_palsu(isi):
    r = MagicMock()
    r.read.return_value = isi
    r.__enter__.return_value = r
    return r


@override_settings(GOOGLE_CLIENT_ID="cid", GOOGLE_CLIENT_SECRET="rahasia")
class CallbackGoogleTest(TestCase):
    def panggil(self, email, host=None):
        session = self.client.session
        session["google_oauth_state"] = "ok"
        session.save()
        token = respons_palsu(b'{"access_token": "tok"}')
        profil = respons_palsu(('{"email": "%s", "name": "Tamu Google"}' % email).encode())
        extra = {"HTTP_HOST": host} if host else {}
        with patch("apps.accounts.views.urllib.request.urlopen", side_effect=[token, profil]):
            return self.client.get(
                reverse("accounts:google_callback") + "?code=c&state=ok", **extra
            )

    def test_callback_google_host_cpns_buat_peserta(self):
        r = self.panggil("tamu@contoh.id", HOST_CPNS)
        self.assertRedirects(r, "/dasbor/", fetch_redirect_response=False)
        user = User.objects.get(email="tamu@contoh.id")
        self.assertEqual(user.role, "peserta")
        self.assertEqual(user.xp, 0)
        self.assertFalse(XPHistory.objects.filter(user=user).exists())
        self.assertTrue(AksesPeserta.objects.get(user=user).via_google)

    def test_callback_google_host_cpns_user_lama_dapat_via_google(self):
        user = User.objects.create_user(username="lama", email="lama@contoh.id", password="x", role="peserta")
        AksesPeserta.objects.create(user=user, via_google=False)
        self.panggil("lama@contoh.id", HOST_CPNS)
        self.assertTrue(AksesPeserta.objects.get(user=user).via_google)
        user.refresh_from_db()
        self.assertEqual(user.role, "peserta")

    @override_settings(GURU_EMAILS=["guru@contoh.id"])
    def test_callback_google_host_cpns_email_guru_tetap_guru(self):
        self.panggil("guru@contoh.id", HOST_CPNS)
        self.assertEqual(User.objects.get(email="guru@contoh.id").role, "guru")

    def test_callback_google_host_utama_tetap_siswa(self):
        r = self.panggil("murid@contoh.id")
        self.assertRedirects(r, reverse("core:home"), fetch_redirect_response=False)
        user = User.objects.get(email="murid@contoh.id")
        self.assertEqual(user.role, "siswa")
        self.assertEqual(user.xp, 50)
        self.assertFalse(AksesPeserta.objects.filter(user=user).exists())
