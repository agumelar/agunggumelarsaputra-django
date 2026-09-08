from django.test import TestCase, Client
from django.urls import reverse


class SubdomainRoutingTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_cpns_subdomain_routes_to_cpns_landing(self):
        """Request to cpns.agunggumelarsaputra.com / should resolve to CPNS landing page."""
        response = self.client.get('/', HTTP_HOST='cpns.agunggumelarsaputra.com')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CPNS')

    def test_cpns_subdomain_dev_host(self):
        """Request to cpns.localhost / should also resolve to CPNS landing page."""
        response = self.client.get('/', HTTP_HOST='cpns.localhost:8000')
        self.assertEqual(response.status_code, 200)

    def test_fallback_cpns_path_on_main_domain(self):
        """Path /cpns/ on main domain should also resolve."""
        response = self.client.get('/cpns/')
        self.assertEqual(response.status_code, 200)
