from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.gamification.services import get_leaderboard_data
from config.settings.base import CPNS_URL_BAWAAN, normalisasi_cpns_url

User = get_user_model()
CPNS_HOST = 'cpns.agunggumelarsaputra.com'


def _tujuan():
    return settings.CPNS_URL + 'dasbor/'


class PesertaDiSitusSekolahTest(TestCase):
    def setUp(self):
        self.peserta = User.objects.create_user(
            username='peserta_iso', email='iso@example.com',
            password='Password123!', role=User.ROLE_PESERTA,
        )
        self.client.force_login(self.peserta)

    def test_peserta_di_situs_sekolah_diarahkan(self):
        for path in ('/', '/pembelajaran/'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 302, path)
            self.assertEqual(response['Location'], _tujuan(), path)

    def test_peserta_boleh_cpns_prefix_dan_logout(self):
        response = self.client.get('/cpns/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], reverse('cpns:dasbor'))
        response = self.client.get(reverse('cpns:dasbor'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(response['Location'], _tujuan())
        self.assertEqual(response['Location'], reverse('core:home'))

        # Setelah logout pengguna anonim: beranda sekolah terbuka, tanpa redirect berulang.
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_peserta_di_host_cpns_tidak_diarahkan(self):
        response = self.client.get('/', HTTP_HOST=CPNS_HOST)
        self.assertNotEqual(response.get('Location'), _tujuan())

    def test_siswa_tidak_terpengaruh(self):
        siswa = User.objects.create_user(
            username='siswa_iso', email='siswa@example.com',
            password='Password123!', role=User.ROLE_SISWA,
        )
        self.client.force_login(siswa)
        for path in ('/', '/pembelajaran/'):
            response = self.client.get(path)
            self.assertNotEqual(response.get('Location'), _tujuan(), path)

    def test_cpns_url_berakhir_garis_miring(self):
        self.assertTrue(settings.CPNS_URL.endswith('/'))
        response = self.client.get('/')
        self.assertEqual(response['Location'], settings.CPNS_URL + 'dasbor/')
        self.assertNotIn('comdasbor', response['Location'])

    def _siswa_dan_peserta(self):
        siswa = User.objects.create_user(
            username='siswa_lb', email='lb@example.com', password='Password123!',
            role=User.ROLE_SISWA, first_name='SiswaTampil', xp=50,
        )
        self.peserta.first_name = 'PesertaRahasia'
        self.peserta.xp = 500
        self.peserta.save()
        return siswa

    def test_peserta_tidak_ada_di_leaderboard(self):
        siswa = self._siswa_dan_peserta()
        data = get_leaderboard_data()
        pks = [u.pk for u in data['ranked_list']]
        self.assertIn(siswa.pk, pks)
        self.assertNotIn(self.peserta.pk, pks)
        self.assertNotIn(self.peserta.pk, [u.pk for u in data['top3']])

    def test_peserta_tidak_ada_di_panel_guru(self):
        self._siswa_dan_peserta()
        guru = User.objects.create_user(
            username='guru_iso', email='guru@example.com',
            password='Password123!', role=User.ROLE_GURU,
        )
        self.client.force_login(guru)
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SiswaTampil')
        self.assertNotContains(response, 'PesertaRahasia')
        self.assertNotContains(response, 'peserta_iso')


class PesertaDiHostCpnsTest(TestCase):
    """Di host cpns rute situs sekolah ikut terpasang; peserta tidak boleh membukanya."""

    def setUp(self):
        self.peserta = User.objects.create_user(
            username='peserta_host', email='host@example.com',
            password='Password123!', role=User.ROLE_PESERTA,
        )
        self.client.force_login(self.peserta)

    def get(self, path):
        return self.client.get(path, HTTP_HOST=CPNS_HOST)

    def test_rute_sekolah_dialihkan_ke_dasbor_cpns(self):
        for path in ('/literasi/', '/pembelajaran/', '/gamification/leaderboard/', '/accounts/profile/'):
            response = self.get(path)
            self.assertEqual(response.status_code, 302, path)
            self.assertEqual(response['Location'], '/dasbor/', path)

    def test_rute_cpns_tidak_dialihkan(self):
        for path in ('/dasbor/', '/premium/'):
            response = self.get(path)
            self.assertEqual(response.status_code, 200, path)

    def test_logout_di_host_cpns(self):
        response = self.get('/accounts/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')
        self.assertNotIn('_auth_user_id', self.client.session)
        response = self.get('/')
        self.assertEqual(response.status_code, 200)

    @override_settings(GOOGLE_CLIENT_ID='cid', GOOGLE_CLIENT_SECRET='rahasia')
    def test_oauth_di_host_cpns_tidak_dialihkan(self):
        response = self.get('/accounts/oauth/google/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('https://accounts.google.com/'))

    def test_path_tidak_dikenal_tetap_404(self):
        self.assertEqual(self.get('/tidak-ada-halaman/').status_code, 404)

    def test_siswa_di_host_cpns_tidak_terpengaruh(self):
        siswa = User.objects.create_user(
            username='siswa_host', email='siswa_host@example.com',
            password='Password123!', role=User.ROLE_SISWA,
        )
        self.client.force_login(siswa)
        for path in ('/literasi/', '/pembelajaran/', '/accounts/profile/'):
            response = self.get(path)
            self.assertNotEqual(response.get('Location'), '/dasbor/', path)

    def test_nav_tanpa_akun_untuk_peserta(self):
        response = self.get('/dasbor/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '>Akun</a>')
        self.assertNotContains(response, '/accounts/profile/')
        self.assertContains(response, '>Keluar</a>', count=2)

    def test_nav_akun_tampil_untuk_siswa_dan_superuser(self):
        siswa = User.objects.create_user(
            username='siswa_nav', email='siswa_nav@example.com',
            password='Password123!', role=User.ROLE_SISWA,
        )
        admin = User.objects.create_superuser(
            username='admin_nav', email='admin_nav@example.com', password='Password123!',
        )
        for user in (siswa, admin):
            self.client.force_login(user)
            response = self.get('/premium/')
            self.assertEqual(response.status_code, 200, user.username)
            self.assertContains(response, '>Akun</a>', count=2)


class NormalisasiCpnsUrlTest(TestCase):
    def test_env_kosong_pakai_bawaan(self):
        self.assertEqual(normalisasi_cpns_url(''), CPNS_URL_BAWAAN)
        self.assertEqual(normalisasi_cpns_url(None), CPNS_URL_BAWAAN)
        self.assertNotEqual(normalisasi_cpns_url(''), '/')

    def test_selalu_satu_garis_miring_di_akhir(self):
        self.assertEqual(normalisasi_cpns_url('http://cpns.localhost:8000'), 'http://cpns.localhost:8000/')
        self.assertEqual(normalisasi_cpns_url('http://cpns.localhost:8000//'), 'http://cpns.localhost:8000/')

    def test_bawaan_berakhir_garis_miring(self):
        self.assertTrue(CPNS_URL_BAWAAN.endswith('/'))
