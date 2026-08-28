from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.admin_panel.models import EnrollmentToken, UserEnrollment

User = get_user_model()


class AuthenticationAndRegistrationTestCase(TestCase):
    def setUp(self):
        # Create a teacher
        self.teacher = User.objects.create_user(
            username='guru_agung',
            email='agung@smkn1rongga.sch.id',
            password='password123',
            first_name='Agung Gumelar',
            last_name='Saputra',
            role=User.ROLE_GURU,
            nip='199001012020011001'
        )

        # Create active enrollment token
        self.token = EnrollmentToken.objects.create(
            token='RPL-TEST',
            title='Sesi KBM Uji Coba',
            target_class='10 RPL 1',
            target_type='all',
            max_uses=36,
            is_active=True,
            created_by=self.teacher
        )

    def test_live_token_validation_htmx(self):
        """Test HTMX endpoint untuk live check token."""
        response = self.client.post(reverse('accounts:check_token'), {'token': 'RPL-TEST'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sesi KBM Uji Coba')
        self.assertContains(response, '10 RPL 1')

        # Test invalid token
        response_invalid = self.client.post(reverse('accounts:check_token'), {'token': 'INVALID-99'})
        self.assertEqual(response_invalid.status_code, 200)
        self.assertContains(response_invalid, 'Kode token tidak ditemukan')

    def test_student_registration_with_valid_token(self):
        """Test pendaftaran siswa berhasil dan dapat +50 XP bonus."""
        data = {
            'token': 'RPL-TEST',
            'name': 'Muhammad Rizky',
            'email': 'rizky@smkn1rongga.sch.id',
            'password': 'password123',
            'password_confirm': 'password123',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertRedirects(response, reverse('core:home'))

        # Verify user
        user = User.objects.get(email='rizky@smkn1rongga.sch.id')
        self.assertTrue(user.is_siswa)
        self.assertEqual(user.first_name, 'Muhammad')
        self.assertEqual(user.last_name, 'Rizky')
        self.assertEqual(user.kelas, '10 RPL 1')
        self.assertEqual(user.xp, 50)
        self.assertEqual(user.level, 1)

        # Verify enrollment
        self.assertTrue(UserEnrollment.objects.filter(user=user, token=self.token).exists())

    def test_registration_with_inactive_token_fails(self):
        """Test pendaftaran ditolak jika token dinonaktifkan."""
        self.token.is_active = False
        self.token.save()

        data = {
            'token': 'RPL-TEST',
            'name': 'Siswa Gagal',
            'email': 'gagal@smkn1rongga.sch.id',
            'password': 'password123',
            'password_confirm': 'password123',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sesi untuk token ini telah dinonaktifkan atau ditutup oleh guru.')
        self.assertFalse(User.objects.filter(email='gagal@smkn1rongga.sch.id').exists())

    def test_universal_login_with_email_and_username(self):
        """Test login fleksibel menggunakan email atau username."""
        # Login dengan Email Guru
        response_guru = self.client.post(reverse('accounts:login'), {
            'identifier': 'agung@smkn1rongga.sch.id',
            'password': 'password123'
        })
        self.assertRedirects(response_guru, reverse('admin_panel:dashboard'))

        self.client.logout()

        # Login dengan Username
        response_user = self.client.post(reverse('accounts:login'), {
            'identifier': 'guru_agung',
            'password': 'password123'
        })
        self.assertRedirects(response_user, reverse('admin_panel:dashboard'))
