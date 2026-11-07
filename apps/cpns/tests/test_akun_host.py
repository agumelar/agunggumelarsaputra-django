from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()
CPNS_HOST = 'cpns.agunggumelarsaputra.com'


class CpnsSubdomainAccountPagesTest(TestCase):
    """Halaman akun memakai navbar utama; di subdomain cpns tidak boleh 500."""

    def test_login_page_renders_on_cpns_subdomain(self):
        response = self.client.get('/accounts/login/', HTTP_HOST=CPNS_HOST)
        self.assertEqual(response.status_code, 200)

    def test_register_page_renders_on_cpns_subdomain(self):
        response = self.client.get('/accounts/register/', HTTP_HOST=CPNS_HOST)
        self.assertEqual(response.status_code, 200)


class LoginNextRedirectTest(TestCase):
    def setUp(self):
        User.objects.create_user(
            username='peserta_next', email='next@example.com',
            password='Password123!', role='student',
        )

    def _login(self, next_url):
        return self.client.post(
            f'/accounts/login/?next={next_url}',
            {'identifier': 'peserta_next', 'password': 'Password123!'},
            HTTP_HOST=CPNS_HOST,
        )

    def test_next_to_same_site_path_is_followed(self):
        response = self._login('/packages/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/packages/')

    def test_next_to_external_site_is_ignored(self):
        response = self._login('https://evil.example.com/')
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('evil.example.com', response['Location'])
