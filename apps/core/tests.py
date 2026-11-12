import re
from io import StringIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


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


class SeedAkunAdminTest(TestCase):
    """Seed jalan di setiap start container. Akun admin tidak boleh punya kata sandi bawaan."""

    PATH_SEED = 'apps/core/management/commands/seed_master_curriculum.py'

    def jalankan_seed(self):
        out = StringIO()
        call_command('seed_master_curriculum', stdout=out)
        return out.getvalue()

    def test_file_seed_tanpa_literal_kata_sandi(self):
        teks = (settings.BASE_DIR / self.PATH_SEED).read_text(encoding='utf-8')
        self.assertIsNone(re.search(r"set_password\(\s*['\"]", teks))
        self.assertNotIn('password:', teks.lower())

    def test_akun_baru_tanpa_kata_sandi(self):
        keluaran = self.jalankan_seed()
        admin = User.objects.get(username='agumelar')
        self.assertTrue(admin.is_superuser)
        self.assertFalse(admin.has_usable_password())
        self.assertFalse(User.objects.get(username='guru_agung').has_usable_password())
        self.assertIn(
            'Akun admin dibuat tanpa kata sandi. Atur dengan: '
            'python manage.py changepassword <username>',
            keluaran,
        )

    def test_akun_yang_sudah_ada_tidak_disentuh(self):
        ada = User.objects.create_user(
            username='agumelar', email='agumelarsaputra@gmail.com',
            password='SandiPemilik-8812', first_name='Nama Pemilik',
        )
        lama = User.objects.create_user(
            username='guru_agung', email='agung@smkn1rongga.sch.id', password='SandiLain-4410',
        )
        sebelum = {u.pk: (u.password, u.first_name, u.is_staff, u.is_superuser) for u in (ada, lama)}
        self.jalankan_seed()
        for u in User.objects.filter(pk__in=sebelum):
            self.assertEqual((u.password, u.first_name, u.is_staff, u.is_superuser), sebelum[u.pk])
        self.assertTrue(User.objects.get(pk=ada.pk).check_password('SandiPemilik-8812'))
