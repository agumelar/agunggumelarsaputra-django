from django.contrib.auth import get_user_model
from django.test import Client, TestCase

CPNS_HOST = 'cpns.agunggumelarsaputra.com'


class SubdomainRoutingTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_beranda_anonim_ke_login_dengan_next(self):
        response = self.client.get('/', HTTP_HOST=CPNS_HOST)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/accounts/login/?next=/')

    def test_beranda_dev_host_anonim_ke_login(self):
        response = self.client.get('/', HTTP_HOST='cpns.localhost:8000')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('/accounts/login/?next='))

    def test_beranda_login_ke_dasbor(self):
        user = get_user_model().objects.create_user(username='rute', email='rute@contoh.id', password='x')
        self.client.force_login(user)
        response = self.client.get('/', HTTP_HOST=CPNS_HOST)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/dasbor/')

    def test_dasbor_di_subdomain(self):
        user = get_user_model().objects.create_user(username='rute2', email='rute2@contoh.id', password='x')
        self.client.force_login(user)
        response = self.client.get('/dasbor/', HTTP_HOST=CPNS_HOST)
        self.assertEqual(response.status_code, 200)

    def test_fallback_cpns_path_on_main_domain(self):
        """Path /cpns/ on main domain should also resolve."""
        response = self.client.get('/cpns/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/accounts/login/?next=/cpns/')

    def test_fallback_main_domain_login_ke_dasbor_berprefiks(self):
        user = get_user_model().objects.create_user(username='rute3', email='rute3@contoh.id', password='x')
        self.client.force_login(user)
        response = self.client.get('/cpns/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/cpns/dasbor/')
