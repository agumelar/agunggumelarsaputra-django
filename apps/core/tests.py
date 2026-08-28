from django.test import TestCase
from django.urls import reverse


class CoreViewsTestCase(TestCase):
    def test_home_page_status_code_and_template(self):
        """Test landing page loads successfully with base M3 template and context."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertContains(response, 'Agung Gumelar Saputra, S.Tr.T.')
        self.assertContains(response, 'Rekayasa Perangkat Lunak')
        self.assertContains(response, 'Pengembangan Perangkat Lunak dan Gim')
