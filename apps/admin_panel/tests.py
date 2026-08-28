from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.admin_panel.models import EnrollmentToken, UserEnrollment

User = get_user_model()


class AdminPanelTestCase(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='guru_agung',
            email='agung@smkn1rongga.sch.id',
            password='password123',
            first_name='Agung Gumelar',
            last_name='Saputra',
            role=User.ROLE_GURU,
            nip='199001012020011001'
        )

        self.student = User.objects.create_user(
            username='siswa_asep',
            email='asep@smkn1rongga.sch.id',
            password='password123',
            role=User.ROLE_SISWA,
            kelas='10 RPL 1'
        )

    def test_student_cannot_access_teacher_dashboard(self):
        """Test siswa ditolak mengakses panel guru."""
        self.client.login(username='siswa_asep', password='password123')
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_teacher_can_access_dashboard_and_create_token(self):
        """Test guru dapat mengakses panel dan membuat token baru."""
        self.client.login(username='guru_agung', password='password123')
        
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 200)

        # Buat token baru
        token_data = {
            'title': 'KBM Pemrograman Web Dasar',
            'target_class': '10 RPL 2',
            'target_type': 'all',
            'custom_token': 'WEB-10RPL2',
            'max_uses': 36,
            'description': 'Praktikum HTML & Tailwind CSS'
        }
        res_create = self.client.post(reverse('admin_panel:token_create'), token_data)
        self.assertRedirects(res_create, reverse('admin_panel:token_list'))

        token = EnrollmentToken.objects.get(token='WEB-10RPL2')
        self.assertEqual(token.title, 'KBM Pemrograman Web Dasar')
        self.assertEqual(token.target_class, '10 RPL 2')
        self.assertTrue(token.is_active)

    def test_teacher_can_toggle_token_status_htmx(self):
        """Test toggle status sesi aktif / ditutup via HTMX."""
        self.client.login(username='guru_agung', password='password123')
        token = EnrollmentToken.objects.create(
            token='TOGGLE-ME',
            title='Test Sesi Toggle',
            target_class='Semua Kelas',
            is_active=True,
            created_by=self.teacher
        )

        response = self.client.post(reverse('admin_panel:token_toggle', kwargs={'token_id': token.id}), HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        token.refresh_from_db()
        self.assertFalse(token.is_active)
        self.assertContains(response, 'Ditutup')
