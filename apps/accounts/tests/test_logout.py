from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()
CPNS_HOST = 'cpns.agunggumelarsaputra.com'


class LogoutPostTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='keluar_u', email='keluar@example.com',
            password='Password123!', role=User.ROLE_PESERTA,
        )
        self.url = reverse('accounts:logout')

    def test_get_tidak_mengeluarkan(self):
        self.client.force_login(self.user)
        r = self.client.get(self.url, HTTP_HOST=CPNS_HOST)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Keluar dari akun?')
        self.assertContains(r, 'method="post"')
        self.assertIn('_auth_user_id', self.client.session)

    def test_get_di_host_cpns_memakai_base_cpns(self):
        self.client.force_login(self.user)
        r = self.client.get('/accounts/logout/', HTTP_HOST=CPNS_HOST)
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'cpns/base_cpns.html')
        self.assertContains(r, 'href="/dasbor/"')

    def test_get_tamu_diarahkan_ke_beranda(self):
        r = self.client.get(self.url)
        self.assertRedirects(r, reverse('core:home'), fetch_redirect_response=False)

    def test_post_mengeluarkan(self):
        self.client.force_login(self.user)
        r = self.client.post(self.url)
        self.assertRedirects(r, reverse('core:home'), fetch_redirect_response=False)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_post_tanpa_csrf_ditolak(self):
        c = Client(enforce_csrf_checks=True)
        c.force_login(self.user)
        r = c.post(self.url)
        self.assertEqual(r.status_code, 403)
        self.assertIn('_auth_user_id', c.session)

    def test_tombol_keluar_berupa_form_post(self):
        guru = User.objects.create_user(
            username='keluar_g', email='g@example.com',
            password='Password123!', role=User.ROLE_SISWA,
        )
        for klien_user, path, host in (
            (self.user, '/dasbor/', CPNS_HOST),
            (guru, reverse('core:home'), 'testserver'),
        ):
            c = Client()
            c.force_login(klien_user)
            html = c.get(path, HTTP_HOST=host).content.decode()
            self.assertNotIn(f'<a href="{self.url}"', html, path)
            self.assertIn(f'<form method="post" action="{self.url}"', html, path)
            self.assertIn('csrfmiddlewaretoken', html, path)
