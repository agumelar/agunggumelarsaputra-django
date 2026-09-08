from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.admin_panel.models import EnrollmentToken, UserEnrollment
from apps.pembelajaran.models import Modul, UserSubmission

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


class SubmissionHubTestCase(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='guru_agung',
            email='agung@smkn1rongga.sch.id',
            password='password123',
            first_name='Agung Gumelar',
            last_name='Saputra',
            role=User.ROLE_GURU,
            nip='199306012022211013'
        )

        self.student = User.objects.create_user(
            username='siswa_budi',
            email='budi@smkn1rongga.sch.id',
            password='password123',
            first_name='Budi',
            last_name='Santoso',
            role=User.ROLE_SISWA,
            kelas='10 RPL 1',
            nisn='0061234567'
        )

        self.modul = Modul.objects.create(
            kode='OR-01',
            judul='Orientasi PPLG & Budaya Kerja Industri',
            slug='orientasi-pplg-budaya-kerja',
            urutan=1
        )

        self.lkpd_submission = UserSubmission.objects.create(
            user=self.student,
            modul=self.modul,
            submission_type='lkpd',
            form_data={'appAudit': [{'namaAplikasi': 'VS Code', 'fitur': 'Code Editor'}]},
            drive_url='https://drive.google.com/drive/folders/test12345',
            status='submitted'
        )

        self.reflection_submission = UserSubmission.objects.create(
            user=self.student,
            modul=self.modul,
            submission_type='reflection',
            form_data={
                'q1': 'Saya memahami pentingnya etika profesi software engineer.',
                'q2': 'Tantangan terbesar adalah konsistensi waktu belajar mandiri.',
                'q3': 'Saya berusaha membagi waktu dengan jadwal terstruktur.',
                'q4': 'Saya ingin mempelajari Git dan arsitektur web modern.'
            },
            status='submitted'
        )

    def test_student_cannot_grade_or_review(self):
        """Test siswa tidak memiliki izin untuk menilai tugas atau meninjau refleksi."""
        self.client.login(username='siswa_budi', password='password123')
        
        # Test grade LKPD
        res_grade = self.client.post(
            reverse('admin_panel:grade_submission_api'),
            data={'submissionId': self.lkpd_submission.id, 'teacherScore': 85},
            content_type='application/json'
        )
        self.assertEqual(res_grade.status_code, 302)

        # Test review Refleksi
        res_review = self.client.post(
            reverse('admin_panel:review_reflection_api'),
            data={'submissionId': self.reflection_submission.id, 'teacherFeedback': 'Bagus'},
            content_type='application/json'
        )
        self.assertEqual(res_review.status_code, 302)

    def test_teacher_grade_lkpd_success(self):
        """Test guru berhasil memberikan nilai LKPD, level KKTP, dan feedback evaluasi."""
        self.client.login(username='guru_agung', password='password123')

        payload = {
            'submissionId': self.lkpd_submission.id,
            'teacherScore': 88,
            'teacherLevel': 'Level 3 (Mampu Membimbing ★★★)',
            'teacherFeedback': 'Analisis aplikasi sangat detail dan terstruktur dengan rapi.'
        }
        response = self.client.post(
            reverse('admin_panel:grade_submission_api'),
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['submission']['isPassed'])

        self.lkpd_submission.refresh_from_db()
        self.assertEqual(self.lkpd_submission.teacher_score, 88)
        self.assertEqual(self.lkpd_submission.status, 'graded')
        self.assertEqual(self.lkpd_submission.graded_by, self.teacher)

    def test_teacher_grade_lkpd_validation(self):
        """Test validasi batas skor nilai (0-100) dan penanganan input tidak valid."""
        self.client.login(username='guru_agung', password='password123')

        # Skor melebihi 100
        res_over = self.client.post(
            reverse('admin_panel:grade_submission_api'),
            data={'submissionId': self.lkpd_submission.id, 'teacherScore': 105},
            content_type='application/json'
        )
        self.assertEqual(res_over.status_code, 400)
        self.assertIn('error', res_over.json())

        # Skor di bawah 0
        res_under = self.client.post(
            reverse('admin_panel:grade_submission_api'),
            data={'submissionId': self.lkpd_submission.id, 'teacherScore': -5},
            content_type='application/json'
        )
        self.assertEqual(res_under.status_code, 400)

        # ID submisi tidak ada
        res_noid = self.client.post(
            reverse('admin_panel:grade_submission_api'),
            data={'teacherScore': 80},
            content_type='application/json'
        )
        self.assertEqual(res_noid.status_code, 400)

    def test_teacher_review_reflection_success(self):
        """Test guru meninjau jurnal refleksi siswa dan memberikan apresiasi kualitatif."""
        self.client.login(username='guru_agung', password='password123')

        payload = {
            'submissionId': self.reflection_submission.id,
            'teacherFeedback': 'Refleksi sangat mendalam dan menunjukkan pemikiran kritis yang baik.'
        }
        response = self.client.post(
            reverse('admin_panel:review_reflection_api'),
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

        self.reflection_submission.refresh_from_db()
        self.assertEqual(self.reflection_submission.status, 'reviewed')
        self.assertEqual(self.reflection_submission.graded_by, self.teacher)
        self.assertIn('Refleksi sangat mendalam', self.reflection_submission.teacher_feedback)

    def test_teacher_export_lkpd_csv(self):
        """Test ekspor rekap nilai LKPD ke CSV (UTF-8 BOM)."""
        self.client.login(username='guru_agung', password='password123')

        # Set nilai tuntas KKM 73
        self.lkpd_submission.teacher_score = 85
        self.lkpd_submission.teacher_level = 'Level 3 (Mampu Membimbing ★★★)'
        self.lkpd_submission.status = 'graded'
        self.lkpd_submission.graded_by = self.teacher
        self.lkpd_submission.save()

        response = self.client.get(reverse('admin_panel:export_lkpd_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response['Content-Type'])
        self.assertIn('charset=utf-8-sig', response['Content-Type'])
        self.assertIn('Rekap_Nilai_LKPD_PPLG_RPL_SMKN1Rongga.csv', response['Content-Disposition'])

        content = response.content.decode('utf-8-sig')
        self.assertIn('Budi Santoso', content)
        self.assertIn('0061234567', content)
        self.assertIn('TUNTAS (TERKUNCI)', content)
        self.assertIn('85', content)

    def test_teacher_export_reflections_csv(self):
        """Test ekspor rekap refleksi siswa ke CSV (UTF-8 BOM)."""
        self.client.login(username='guru_agung', password='password123')

        response = self.client.get(reverse('admin_panel:export_reflections_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response['Content-Type'])
        self.assertIn('charset=utf-8-sig', response['Content-Type'])
        self.assertIn('Rekap_Jurnal_Refleksi_RPL_SMKN1Rongga.csv', response['Content-Disposition'])

        content = response.content.decode('utf-8-sig')
        self.assertIn('Budi Santoso', content)
        self.assertIn('Saya memahami pentingnya etika profesi', content)

