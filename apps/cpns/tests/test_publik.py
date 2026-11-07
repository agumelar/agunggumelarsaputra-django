from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.cpns.models import PengaturanCPNS, SkemaBagian, SkemaUjian

CPNS_HOST = 'cpns.agunggumelarsaputra.com'


class BerandaPublikTest(TestCase):
    def ambil(self, nama='cpns:beranda'):
        return self.client.get(reverse(nama))

    def test_tamu_melihat_beranda_publik(self):
        r = self.ambil()
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Daftar dan coba gratis')
        self.assertContains(r, 'Saya sudah punya akun')
        self.assertContains(r, 'Tidak berafiliasi dengan BKN')
        self.assertContains(r, reverse('cpns:daftar'))
        self.assertContains(r, reverse('cpns:masuk'))

    def test_login_diarahkan_ke_dasbor(self):
        user = get_user_model().objects.create_user(username='p6', email='p6@contoh.id', password='x')
        self.client.force_login(user)
        r = self.ambil()
        self.assertRedirects(r, reverse('cpns:dasbor'), fetch_redirect_response=False)

    def test_ambang_dari_database(self):
        SkemaBagian.objects.filter(skema__kode='SKD-CAT', subtes='TWK').update(ambang_batas=70)
        self.assertContains(self.ambil(), 'Ambang 70')

    def test_cara_nilai_tkp_dan_lainnya(self):
        r = self.ambil()
        self.assertContains(r, '1 sampai 5 per soal')
        self.assertContains(r, 'benar 5, salah 0')

    def test_skema_hilang_bagian_disembunyikan(self):
        SkemaUjian.objects.filter(kode='SKD-CAT').delete()
        r = self.ambil()
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, 'Cara nilai SKD')

    def test_harga_kosong_teks_jujur(self):
        p = PengaturanCPNS.ambil()
        p.teks_harga = {}
        p.save()
        self.assertContains(self.ambil(), 'Harga Premium: hubungi admin.')

    def test_harga_terisi_tampil(self):
        p = PengaturanCPNS.ambil()
        p.teks_harga = {'30': 'Rp 49.000'}
        p.save()
        r = self.ambil()
        self.assertContains(r, 'Rp 49.000')
        self.assertContains(r, '30 hari')
        self.assertNotContains(r, 'Harga Premium: hubungi admin.')


class BerandaHostCpnsTest(TestCase):
    def test_tamu_di_host_cpns(self):
        r = self.client.get('/', HTTP_HOST=CPNS_HOST)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'href="/syarat-layanan/"')
        self.assertContains(r, 'href="/kebijakan-privasi/"')


class HalamanHukumTest(TestCase):
    def test_syarat_dan_privasi_200_dan_footer_tertaut(self):
        for nama in ('cpns:syarat', 'cpns:privasi'):
            r = self.client.get(reverse(nama))
            self.assertEqual(r.status_code, 200, nama)
            self.assertContains(r, 'Draf, menunggu tinjauan pengelola.')
            self.assertContains(r, '[NAMA DAN KONTAK PENGELOLA]')
            self.assertContains(r, f'href="{reverse("cpns:syarat")}"')
            self.assertContains(r, f'href="{reverse("cpns:privasi")}"')
        r = self.client.get(reverse('cpns:syarat'))
        self.assertContains(r, '[KEBIJAKAN PENGEMBALIAN DANA]')

    def test_tanpa_klaim_resmi_publik(self):
        for nama in ('cpns:beranda', 'cpns:syarat', 'cpns:privasi'):
            teks = self.client.get(reverse(nama)).content.decode().lower()
            self.assertNotIn('resmi', teks, nama)
            self.assertNotIn('soal asli', teks, nama)
            self.assertNotIn('—', teks, nama)

    def test_footer_tanpa_literal_lama(self):
        r = self.client.get(reverse('cpns:syarat'))
        self.assertNotContains(r, 'href="/syarat-layanan/"')
