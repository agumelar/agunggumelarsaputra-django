from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
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

    @override_settings(GOOGLE_CLIENT_ID='', GOOGLE_CLIENT_SECRET='')
    def test_google_oauth_login_unconfigured_redirect(self):
        """Test Google OAuth login redirects to login page with warning when not configured."""
        response = self.client.get(reverse('accounts:google_login'))
        self.assertRedirects(response, reverse('accounts:login'))

    @override_settings(GOOGLE_CLIENT_ID='test-client-id.apps.googleusercontent.com', GOOGLE_CLIENT_SECRET='test-secret')
    def test_google_oauth_login_configured_redirect(self):
        """Test Google OAuth login redirects to Google accounts URL when configured."""
        response = self.client.get(reverse('accounts:google_login'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('https://accounts.google.com/o/oauth2/v2/auth'))
        self.assertIn('test-client-id', response.url)
        self.assertIn('google_oauth_state', self.client.session)

    def test_google_oauth_callback_state_mismatch(self):
        """Test OAuth callback fails safely if state does not match."""
        session = self.client.session
        session['google_oauth_state'] = 'correct-state'
        session.save()

        response = self.client.get(reverse('accounts:google_callback') + '?code=test-code&state=wrong-state')
        self.assertRedirects(response, reverse('accounts:login'))

    @override_settings(GOOGLE_CLIENT_ID='test-client-id', GOOGLE_CLIENT_SECRET='test-secret')
    @patch('urllib.request.urlopen')
    def test_google_oauth_callback_creates_student_user(self, mock_urlopen):
        """Test Google OAuth callback creates a new student user with +50 XP bonus."""
        session = self.client.session
        session['google_oauth_state'] = 'valid-state'
        session.save()

        # Mock token response
        token_response = MagicMock()
        token_response.read.return_value = b'{"access_token": "mock-token-xyz"}'
        token_response.__enter__.return_value = token_response

        # Mock userinfo response
        userinfo_response = MagicMock()
        userinfo_response.read.return_value = b'{"email": "student.baru@smkn1rongga.sch.id", "name": "Siswa Baru Google", "sub": "google-id-123"}'
        userinfo_response.__enter__.return_value = userinfo_response

        mock_urlopen.side_effect = [token_response, userinfo_response]

        response = self.client.get(reverse('accounts:google_callback') + '?code=valid-code&state=valid-state')
        self.assertRedirects(response, reverse('core:home'))

        # Verify created user
        new_user = User.objects.get(email='student.baru@smkn1rongga.sch.id')
        self.assertTrue(new_user.is_siswa)
        self.assertEqual(new_user.first_name, 'Siswa')
        self.assertEqual(new_user.last_name, 'Baru Google')
        self.assertEqual(new_user.xp, 50)

    def test_is_profile_complete_property(self):
        """Test properti is_profile_complete untuk Guru dan Siswa."""
        # Guru selalu lengkap
        self.assertTrue(self.teacher.is_profile_complete)

        # Siswa tanpa kelas dan tanpa foto: tidak lengkap
        student = User.objects.create_user(
            username='siswa_test',
            email='siswa_test@smkn1rongga.sch.id',
            password='password123',
            role=User.ROLE_SISWA,
            kelas='',
            avatar=None,
            avatar_url=''
        )
        self.assertFalse(student.is_profile_complete)

        # Siswa punya kelas tapi belum punya foto: tidak lengkap
        student.kelas = '10 RPL 1'
        student.save()
        self.assertFalse(student.is_profile_complete)

        # Siswa punya kelas dan foto URL: lengkap
        student.avatar_url = 'https://example.com/photo.jpg'
        student.save()
        self.assertTrue(student.is_profile_complete)

    def test_complete_profile_api_success(self):
        """Test API complete-profile berhasil menyimpan nama, kelas, dan base64 avatar."""
        student = User.objects.create_user(
            username='siswa_incomplete',
            email='incomplete@smkn1rongga.sch.id',
            password='password123',
            role=User.ROLE_SISWA
        )
        self.client.force_login(student)

        # Base64 data url dummy 1x1 pixel PNG
        dummy_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        payload = {
            'name': 'Anita Sri Devi',
            'kelas': '11 RPL 2',
            'avatar_data': dummy_base64
        }
        response = self.client.post(
            reverse('accounts:complete_profile_api'),
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))

        # Refresh student
        student.refresh_from_db()
        self.assertEqual(student.first_name, 'Anita')
        self.assertEqual(student.last_name, 'Sri Devi')
        self.assertEqual(student.kelas, '11 RPL 2')
        self.assertTrue(bool(student.avatar))
        self.assertTrue(student.is_profile_complete)

    def test_complete_profile_api_validation_errors(self):
        """Test validasi pada API complete-profile jika nama, kelas, atau foto tidak valid."""
        student = User.objects.create_user(
            username='siswa_val',
            email='val@smkn1rongga.sch.id',
            password='password123',
            role=User.ROLE_SISWA
        )
        self.client.force_login(student)

        # 1. Nama kosong / kurang dari 2 karakter
        res1 = self.client.post(
            reverse('accounts:complete_profile_api'),
            data={'name': 'A', 'kelas': '10 RPL 1', 'avatar_data': ''},
            content_type='application/json'
        )
        self.assertEqual(res1.status_code, 400)
        self.assertIn('minimal 2 karakter', res1.json().get('error', ''))

        # 2. Kelas tidak valid
        res2 = self.client.post(
            reverse('accounts:complete_profile_api'),
            data={'name': 'Budi Santoso', 'kelas': '99 RPL FAKE', 'avatar_data': ''},
            content_type='application/json'
        )
        self.assertEqual(res2.status_code, 400)
        self.assertIn('Kelas / Rombel yang valid', res2.json().get('error', ''))

        # 3. Avatar kosong
        res3 = self.client.post(
            reverse('accounts:complete_profile_api'),
            data={'name': 'Budi Santoso', 'kelas': '10 RPL 1', 'avatar_data': ''},
            content_type='application/json'
        )
        self.assertEqual(res3.status_code, 400)
        self.assertIn('pas foto profil', res3.json().get('error', ''))

    def test_profile_form_includes_kelas_for_students(self):
        """Test form profil mengikutsertakan dan memvalidasi kelas untuk siswa."""
        from apps.accounts.forms import UserProfileForm

        student = User.objects.create_user(
            username='siswa_form',
            email='form@smkn1rongga.sch.id',
            password='password123',
            role=User.ROLE_SISWA,
            kelas='10 RPL 3'
        )
        form = UserProfileForm(instance=student)
        self.assertIn('kelas', form.fields)
        self.assertTrue(form.fields['kelas'].required)

        # Test valid submission
        post_data = {
            'first_name': 'Ahmad',
            'last_name': 'Dahlan',
            'kelas': '12 RPL 1',
            'bio': 'Belajar Django',
            'github_username': 'ahmad123'
        }
        form_post = UserProfileForm(data=post_data, instance=student)
        self.assertTrue(form_post.is_valid())
        updated_user = form_post.save()
        self.assertEqual(updated_user.kelas, '12 RPL 1')

