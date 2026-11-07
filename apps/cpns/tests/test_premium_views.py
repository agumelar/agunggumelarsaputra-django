from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.dateformat import format as format_tanggal

from apps.cpns.models import AksesPeserta, PengaturanCPNS, PercobaanVoucher
from apps.cpns.voucher import buat_voucher

HX = {"HTTP_HX_REQUEST": "true"}
SALAH = "Kode tidak ditemukan atau sudah dipakai. Periksa lagi huruf dan angkanya."


def buat_user(username):
    user = get_user_model().objects.create_user(
        username=username, email=f"{username}@contoh.id", password="x"
    )
    AksesPeserta.objects.create(user=user, via_google=True)
    return user


def atur(nomor="6281234567890", harga=None):
    p = PengaturanCPNS.ambil()
    p.nomor_wa = nomor
    p.teks_harga = {"30": "Rp 50.000", "90": "Rp 120.000"} if harga is None else harga
    p.save()


class PremiumHalamanTests(TestCase):
    def setUp(self):
        self.url = reverse("cpns:premium")

    def test_premium_tamu_200_tanpa_form(self):
        atur()
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, 'name="kode"')
        self.assertContains(r, "Masuk untuk menukar kode")
        self.assertContains(r, "Rp 50.000")
        self.assertContains(r, "Cara membeli")

    def test_premium_tautan_wa_ada_dan_aman(self):
        atur()
        user = buat_user("budi")
        self.client.force_login(user)
        r = self.client.get(self.url)
        html = r.content.decode()
        self.assertIn('href="https://wa.me/6281234567890?text=', html)
        self.assertIn('rel="noopener"', html)
        self.assertIn('target="_blank"', html)
        self.assertIn("budi%40contoh.id", html)
        self.assertContains(r, "Hubungi admin via WhatsApp")
        self.assertContains(r, 'name="kode"')
        self.assertContains(r, 'role="status"')
        self.assertContains(r, "Akun Trial")

    def test_premium_tanpa_nomor_wa(self):
        atur(nomor="")
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, "wa.me")
        self.assertContains(r, "Kontak admin belum diatur.")

    def test_premium_tanpa_harga(self):
        atur(harga={})
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, "[HARGA]")

    def test_premium_menampilkan_tanggal_berakhir(self):
        atur()
        user = buat_user("sari")
        akses = user.akses_cpns
        akses.premium_sampai = timezone.now() + timedelta(days=10)
        akses.save()
        self.client.force_login(user)
        r = self.client.get(self.url)
        self.assertContains(r, "Premium sampai " + format_tanggal(timezone.localtime(akses.premium_sampai), "d M Y"))


class TukarVoucherTests(TestCase):
    def setUp(self):
        self.url = reverse("cpns:tukar_voucher")
        self.user = buat_user("budi")
        self.client.force_login(self.user)

    def kirim(self, kode, **ekstra):
        return self.client.post(self.url, {"kode": kode}, **ekstra)

    def test_tukar_berhasil_htmx(self):
        v = buat_voucher(1, 30)[0]
        r = self.kirim(v.kode.lower(), **HX)
        self.assertEqual(r.status_code, 200)
        self.user.akses_cpns.refresh_from_db()
        tgl = format_tanggal(timezone.localtime(self.user.akses_cpns.premium_sampai), "d M Y")
        self.assertContains(r, f"Premium aktif sampai {tgl}.")

    def test_tukar_berhasil_tanpa_htmx_redirect_dengan_pesan(self):
        v = buat_voucher(1, 30)[0]
        r = self.kirim(v.kode)
        self.assertRedirects(r, reverse("cpns:premium"), fetch_redirect_response=False)
        teks = [m.message for m in r.wsgi_request._messages]
        self.assertTrue(any(t.startswith("Premium aktif sampai ") for t in teks))

    def test_tukar_salah_menampilkan_sisa(self):
        r = self.kirim("ZZZZ-ZZZZ", **HX)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, SALAH + " Sisa percobaan: 4 dari 5 per jam.")

    def test_tukar_salah_tanpa_htmx(self):
        r = self.kirim("ZZZZ-ZZZZ")
        self.assertRedirects(r, reverse("cpns:premium"), fetch_redirect_response=False)
        teks = [m.message for m in r.wsgi_request._messages]
        self.assertIn(SALAH + " Sisa percobaan: 4 dari 5 per jam.", teks)

    def test_tukar_terlalu_sering(self):
        for _ in range(5):
            PercobaanVoucher.objects.create(user=self.user, waktu=timezone.now(), berhasil=False)
        r = self.kirim("ZZZZ-ZZZZ", **HX)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Terlalu banyak percobaan. Coba lagi dalam satu jam.")

    def test_tukar_kosong_atau_kepanjangan_400_htmx(self):
        for kode in ("", "   ", "A" * 21):
            r = self.kirim(kode, **HX)
            self.assertEqual(r.status_code, 400)
        self.assertEqual(PercobaanVoucher.objects.count(), 0)

    def test_tukar_kosong_tanpa_htmx(self):
        r = self.kirim("")
        self.assertRedirects(r, reverse("cpns:premium"), fetch_redirect_response=False)
        self.assertEqual(PercobaanVoucher.objects.count(), 0)

    def test_tukar_get_ditolak(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 405)

    def test_tukar_tamu_diarahkan_ke_masuk(self):
        self.client.logout()
        r = self.kirim("ABCD-EFGH")
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("cpns:masuk"), r["Location"])

    def test_tukar_dua_kali_kode_sama(self):
        v = buat_voucher(1, 30)[0]
        self.assertEqual(self.kirim(v.kode, **HX).status_code, 200)
        lain = buat_user("sari")
        self.client.force_login(lain)
        r = self.kirim(v.kode, **HX)
        self.assertContains(r, SALAH)
        self.assertIsNone(lain.akses_cpns.premium_sampai)
