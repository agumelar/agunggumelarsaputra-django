from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.gamification.services import get_leaderboard_data

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
        response = self.client.get('/cpns/')
        self.assertNotEqual(response.get('Location'), _tujuan())

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
