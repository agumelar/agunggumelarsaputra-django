from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.admin_panel.models import EnrollmentToken, UserEnrollment
from apps.pembelajaran.models import Modul, UserSubmission
from apps.literasi.models import LiterasiReport
from apps.tka.models import TkaPackage, TkaAttempt

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


class SinglePaneCommandCenterTestCase(TestCase):
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

        self.other_teacher = User.objects.create_user(
            username='guru_budi',
            email='budi_guru@smkn1rongga.sch.id',
            password='password123',
            first_name='Budi',
            last_name='Guru',
            role=User.ROLE_GURU,
            nip='199501012022211002'
        )

        self.student = User.objects.create_user(
            username='siswa_cici',
            email='cici@smkn1rongga.sch.id',
            password='password123',
            first_name='Cici',
            last_name='Paramida',
            role=User.ROLE_SISWA,
            kelas='10 RPL 1',
            nisn='0071234567'
        )

        self.token = EnrollmentToken.objects.create(
            token='TEST-TOKEN-1',
            title='Sesi KBM Ujian TKA RPL',
            target_class='10 RPL 1',
            target_type='all',
            is_active=True,
            created_by=self.teacher
        )

        # Enrolled student
        UserEnrollment.objects.create(
            token=self.token,
            user=self.student
        )

        # TKA Package & Attempt
        self.tka_package = TkaPackage.objects.create(
            kode='TKA-01',
            judul='Dasar Pemrograman RPL',
            slug='dasar-pemrograman-rpl',
            passing_grade=73,
            urutan=1
        )

        self.tka_attempt = TkaAttempt.objects.create(
            user=self.student,
            package=self.tka_package,
            token=self.token,
            score=84.0,
            total_questions=25,
            correct_answers=21,
            wrong_answers=4,
            is_passed=True,
            time_spent_seconds=1200
        )

        # Literasi Report
        self.literasi_report = LiterasiReport.objects.create(
            user=self.student,
            token=self.token,
            week_number=1,
            book_title='Clean Code in Python',
            author='Mariano Anaya',
            publisher='Packt',
            page_count='1-30',
            word_count=180,
            summary='Rangkuman tentang Clean Code dan prinsip refactoring dalam pengembangan software.',
            moral_message='Kode yang rapi mempermudah kolaborasi tim software engineer.'
        )

    def test_reset_student_password_unauthorized(self):
        """Siswa dilarang mereset password melalui API reset password guru."""
        self.client.login(username='siswa_cici', password='password123')
        res = self.client.post(
            reverse('admin_panel:reset_student_password_api'),
            data={'targetUserId': self.student.id, 'newPassword': 'newpassword123'},
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 302)

    def test_reset_student_password_validation(self):
        """Validasi panjang password minimal 6 karakter dan target user wajib."""
        self.client.login(username='guru_agung', password='password123')

        # Password kurang dari 6 karakter
        res_short = self.client.post(
            reverse('admin_panel:reset_student_password_api'),
            data={'targetUserId': self.student.id, 'newPassword': '123'},
            content_type='application/json'
        )
        self.assertEqual(res_short.status_code, 400)
        self.assertIn('error', res_short.json())

        # Target user tidak disertakan
        res_no_user = self.client.post(
            reverse('admin_panel:reset_student_password_api'),
            data={'newPassword': 'newpassword123'},
            content_type='application/json'
        )
        self.assertEqual(res_no_user.status_code, 400)

    def test_reset_student_password_cannot_reset_teacher_unless_superuser(self):
        """Guru biasa tidak boleh mereset sesama guru/staff."""
        self.client.login(username='guru_agung', password='password123')
        res = self.client.post(
            reverse('admin_panel:reset_student_password_api'),
            data={'targetUserId': self.other_teacher.id, 'newPassword': 'newpassword123'},
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn('Super Admin', res.json()['error'])

    def test_reset_student_password_success(self):
        """Guru berhasil mereset password akun siswa."""
        self.client.login(username='guru_agung', password='password123')
        res = self.client.post(
            reverse('admin_panel:reset_student_password_api'),
            data={'targetUserId': self.student.id, 'newPassword': 'rahasiaBaru123'},
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['success'])

        # Verifikasi autentikasi dengan password baru siswa
        login_success = self.client.login(username='siswa_cici', password='rahasiaBaru123')
        self.assertTrue(login_success)

    def test_token_report_api(self):
        """Endpoint token report API mengembalikan statistik dan data peserta sesi token."""
        self.client.login(username='guru_agung', password='password123')
        res = self.client.get(reverse('admin_panel:token_report_api', kwargs={'token_id': self.token.id}))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['stats']['totalEnrolled'], 1)
        self.assertEqual(data['stats']['totalExamTaken'], 1)
        self.assertEqual(data['stats']['avgScore'], 84)
        self.assertEqual(data['stats']['passCount'], 1)
        self.assertEqual(data['stats']['passRate'], 100)
        self.assertEqual(len(data['students']), 1)
        self.assertEqual(data['students'][0]['name'], 'Cici Paramida')
        self.assertEqual(data['students'][0]['examScore'], 84.0)

    def test_token_export_excel(self):
        """Ekspor data peserta sesi token ke format CSV UTF-8 BOM."""
        self.client.login(username='guru_agung', password='password123')
        res = self.client.get(reverse('admin_panel:export_token_excel', kwargs={'token_id': self.token.id}))
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/csv', res['Content-Type'])
        self.assertIn('charset=utf-8-sig', res['Content-Type'])
        self.assertIn(f'Rekap_Sesi_Token_{self.token.token}.csv', res['Content-Disposition'])

        content = res.content.decode('utf-8-sig')
        self.assertIn('Cici Paramida', content)
        self.assertIn('84.0', content)
        self.assertIn('TUNTAS', content)

    def test_token_delete(self):
        """Guru menghapus sesi token."""
        self.client.login(username='guru_agung', password='password123')
        token_id = self.token.id
        res = self.client.post(reverse('admin_panel:token_delete', kwargs={'token_id': token_id}))
        self.assertRedirects(res, reverse('admin_panel:dashboard'))
        self.assertFalse(EnrollmentToken.objects.filter(id=token_id).exists())

    def test_grade_literasi_api_validation(self):
        """Validasi payload penilaian literasi RESIK."""
        self.client.login(username='guru_agung', password='password123')

        # Tanpa reportId
        res_no_id = self.client.post(
            reverse('admin_panel:grade_literasi_api'),
            data={'w1': 3},
            content_type='application/json'
        )
        self.assertEqual(res_no_id.status_code, 400)

        # Nilai bukan angka
        res_invalid = self.client.post(
            reverse('admin_panel:grade_literasi_api'),
            data={'reportId': self.literasi_report.id, 'w1': 'abc'},
            content_type='application/json'
        )
        self.assertEqual(res_invalid.status_code, 400)

    def test_grade_literasi_api_success(self):
        """Guru menilai 9 rubrik aspek literasi RESIK dengan kalkulasi otomatis."""
        self.client.login(username='guru_agung', password='password123')

        payload = {
            'reportId': self.literasi_report.id,
            'w1': 4, 'w2': 3, 'w3': 4, 'w4': 3,  # Total W = 14
            'p1': 4, 'p2': 4, 'p3': 3, 'p4': 4, 'p5': 3,  # Total P = 18
            'teacherFeedback': 'Ulasan sangat komprehensif dan implementatif.'
        }
        res = self.client.post(
            reverse('admin_panel:grade_literasi_api'),
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        # Expected score: round(((14 + 18) / 36) * 100, 1) = round(32/36 * 100, 1) = 88.9
        self.assertEqual(data['report']['writingScore'], 14)
        self.assertEqual(data['report']['presentationScore'], 18)
        self.assertEqual(data['report']['finalScore'], 88.9)
        self.assertTrue(data['report']['isPassed'])

        self.literasi_report.refresh_from_db()
        self.assertEqual(self.literasi_report.status, 'graded')
        self.assertEqual(self.literasi_report.writing_score, 14)
        self.assertEqual(self.literasi_report.presentation_score, 18)
        self.assertEqual(self.literasi_report.final_score, 88.9)
        self.assertEqual(self.literasi_report.graded_by, self.teacher)

    def test_export_literasi_excel(self):
        """Ekspor rekapitulasi Rabu Literasi RESIK ke format CSV UTF-8 BOM."""
        self.client.login(username='guru_agung', password='password123')

        # Tandai report sudah dinilai
        self.literasi_report.writing_score = 14
        self.literasi_report.presentation_score = 18
        self.literasi_report.final_score = 88.9
        self.literasi_report.status = 'graded'
        self.literasi_report.graded_by = self.teacher
        self.literasi_report.save()

        res = self.client.get(reverse('admin_panel:export_literasi_excel'))
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/csv', res['Content-Type'])
        self.assertIn('charset=utf-8-sig', res['Content-Type'])
        self.assertIn('Rekap_Rabu_Literasi_RESIK_RPL_SMKN1Rongga.csv', res['Content-Disposition'])

        content = res.content.decode('utf-8-sig')
        self.assertIn('Cici Paramida', content)
        self.assertIn('Clean Code in Python', content)
        self.assertIn('88.9', content)

    def test_export_tka_excel(self):
        """Ekspor rekapitulasi ujian CBT TKA ke format CSV UTF-8 BOM."""
        self.client.login(username='guru_agung', password='password123')

        res = self.client.get(reverse('admin_panel:export_tka_excel'))
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/csv', res['Content-Type'])
        self.assertIn('charset=utf-8-sig', res['Content-Type'])
        self.assertIn('Rekap_Nilai_CBT_TKA_PPLG_SMKN1Rongga.csv', res['Content-Disposition'])

        content = res.content.decode('utf-8-sig')
        self.assertIn('Cici Paramida', content)
        self.assertIn('Dasar Pemrograman RPL', content)
        self.assertIn('84.0', content)
        self.assertIn('KOMPETEN (LULUS)', content)

