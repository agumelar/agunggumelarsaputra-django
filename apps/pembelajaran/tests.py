from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.pembelajaran.models import Modul, UserSubmission, UserProgress
from apps.admin_panel.models import EnrollmentToken

User = get_user_model()


class PembelajaranModuleTestCase(TestCase):
    def setUp(self):
        # Create Teacher
        self.teacher = User.objects.create_user(
            username='guru_agung',
            email='agung@smkn1rongga.sch.id',
            password='password123',
            first_name='Agung Gumelar',
            last_name='Saputra',
            role=User.ROLE_GURU,
            nip='199001012020011001'
        )

        # Create Student
        self.student = User.objects.create_user(
            username='siswa_fauzi',
            email='fauzi@smkn1rongga.sch.id',
            password='password123',
            first_name='Ahmad',
            last_name='Fauzi',
            role=User.ROLE_SISWA,
            kelas='10 RPL 1',
            xp=50
        )

        # Create Module
        self.modul = Modul.objects.create(
            kode='OR-01',
            judul='Orientasi Mapel & Sistem Skill Passport PPLG',
            slug='orientasi-pplg-01-pengantar-skill-passport',
            kategori='Orientasi PPLG (OR-01)',
            level='Pemula',
            durasi='2 JP (90 Menit)',
            deskripsi='Pengantar pembelajaran Fase E RPL',
            content_materi='## Selamat Datang di RPL SMKN 1 Rongga',
            teacher_tip='Pastikan link folder Google Drive disetel ke Anyone with link can view.',
            urutan=1,
            xp_materi=10,
            xp_lkpd=25,
            xp_reflection=15,
            is_published=True
        )

    def test_modul_list_view(self):
        """Test modul_list_view returns 200 and contains module title."""
        response = self.client.get(reverse('pembelajaran:modul_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Orientasi Mapel')
        self.assertContains(response, 'OR-01')

    def test_modul_detail_view(self):
        """Test modul_detail_view renders 4-Tab reader."""
        response = self.client.get(reverse('pembelajaran:modul_detail', kwargs={'slug': self.modul.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Materi')
        self.assertContains(response, 'Form LKPD')
        self.assertContains(response, 'Jurnal Refleksi')
        self.assertContains(response, 'Panduan KKTP')
        self.assertContains(response, 'TIPS & CATATAN PAK AGUNG')

    def test_mark_material_read_awards_xp(self):
        """Test siswa menandai materi selesai dan mendapatkan +10 XP."""
        self.client.login(username='siswa_fauzi', password='password123')
        initial_xp = self.student.xp

        response = self.client.post(reverse('pembelajaran:mark_read', kwargs={'slug': self.modul.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Materi Modul Telah Selesai Dibaca!')

        self.student.refresh_from_db()
        self.assertEqual(self.student.xp, initial_xp + 10)
        self.assertTrue(UserProgress.objects.filter(user=self.student, modul=self.modul).exists())

    def test_submit_lkpd_awards_xp(self):
        """Test siswa mengirim LKPD dengan link Google Drive dan mendapatkan +25 XP."""
        self.client.login(username='siswa_fauzi', password='password123')
        initial_xp = self.student.xp

        data = {
            'drive_url': 'https://drive.google.com/drive/folders/1abcXYZ_example',
            'work_summary': 'Telah menyelesaikan audit perangkat lunak 24 jam dan membuat mind map profesi.',
            'additional_notes': 'Mohon feedback untuk struktur folder drive saya.',
        }
        response = self.client.post(reverse('pembelajaran:submit_lkpd', kwargs={'slug': self.modul.slug}), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Google Drive Evidence berhasil dikirim!')

        self.student.refresh_from_db()
        self.assertEqual(self.student.xp, initial_xp + 25)

        submission = UserSubmission.objects.get(user=self.student, modul=self.modul, submission_type='lkpd')
        self.assertEqual(submission.drive_url, 'https://drive.google.com/drive/folders/1abcXYZ_example')
        self.assertEqual(submission.status, 'submitted')

    def test_submit_reflection_awards_xp(self):
        """Test siswa mengirim 3 isian jurnal refleksi dan mendapatkan +15 XP."""
        self.client.login(username='siswa_fauzi', password='password123')
        initial_xp = self.student.xp

        data = {
            'understanding': 'Saya memahami pentingnya etos kerja software engineer.',
            'obstacle': 'Sedikit kesulitan pada pengelompokan framework review.',
            'action_plan': 'Membaca ulang modul 10 dan 11.',
        }
        response = self.client.post(reverse('pembelajaran:submit_refleksi', kwargs={'slug': self.modul.slug}), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jurnal Refleksi berhasil disimpan!')

        self.student.refresh_from_db()
        self.assertEqual(self.student.xp, initial_xp + 15)

    def test_teacher_grading_workflow(self):
        """Test alur penilaian LKPD oleh guru pengampu."""
        # Student submits LKPD
        submission = UserSubmission.objects.create(
            user=self.student,
            modul=self.modul,
            submission_type='lkpd',
            drive_url='https://drive.google.com/drive/folders/test12345',
            form_data={'work_summary': 'Pekerjaan selesai lengkap.'},
            status='submitted'
        )

        # Teacher logs in and grades
        self.client.login(username='guru_agung', password='password123')
        
        grade_data = {
            'teacher_level': 'Level 3',
            'teacher_score': 90,
            'teacher_feedback': 'Struktur rapi, analisis orisinal dan komprehensif. Kerja bagus!',
        }
        response = self.client.post(reverse('admin_panel:grade_submission', kwargs={'submission_id': submission.id}), grade_data)
        self.assertRedirects(response, reverse('admin_panel:submission_list'))

        submission.refresh_from_db()
        self.assertEqual(submission.status, 'graded')
        self.assertEqual(submission.teacher_level, 'Level 3')
        self.assertEqual(submission.teacher_score, 90)
        self.assertEqual(submission.graded_by, self.teacher)

    def test_all_interactive_modules_render(self):
        """Memverifikasi bahwa seluruh modul 1 s/d 16 dapat me-render template interaktifnya tanpa error."""
        self.client.login(username='guru_agung', password='password123')
        for i in range(1, 17):
            m, _ = Modul.objects.get_or_create(
                urutan=i,
                defaults={
                    'kode': f'OR-{i:02d}',
                    'judul': f'Modul Pembelajaran {i:02d}',
                    'slug': f'orientasi-pplg-{i:02d}-test',
                    'kategori': f'Orientasi PPLG (OR-{i:02d})',
                    'level': 'Pemula',
                    'durasi': '2 JP (90 Menit)',
                    'deskripsi': f'Deskripsi modul {i}',
                    'content_materi': f'## Materi Modul {i}',
                    'teacher_tip': f'Tip Guru untuk Modul {i}',
                    'is_published': True,
                }
            )
            response = self.client.get(reverse('pembelajaran:modul_detail', kwargs={'slug': m.slug}))
            self.assertEqual(response.status_code, 200, f"Modul {i} failed to render")
            self.assertContains(response, 'checkpoint-challenge-area')

    def test_structured_lkpd_submission_module_2(self):
        """Memverifikasi pengisian formulir LKPD terstruktur untuk Modul 02."""
        self.client.login(username='siswa_fauzi', password='password123')
        modul2, _ = Modul.objects.get_or_create(
            urutan=2,
            defaults={
                'kode': 'OR-02',
                'judul': '8 Profesi Utama & Sinergi Tim Industri PPLG',
                'slug': 'orientasi-pplg-02-profesi-peluang-karier',
                'kategori': 'Orientasi PPLG (OR-02)',
                'level': 'Pemula',
                'durasi': '2 JP (90 Menit)',
                'deskripsi': 'Analisis profesi TI',
                'content_materi': '## Profesi PPLG',
                'teacher_tip': 'Pilih 3 profesi yang paling diminati.',
                'is_published': True,
            }
        )
        post_data = {
            'drive_url': 'https://drive.google.com/drive/folders/test_evidence_modul2',
            'profession1Name': 'Backend Developer',
            'profession1Responsibilities': 'Membuat REST API dan mengelola basis data.',
            'profession1Tools': 'Python, Django, PostgreSQL',
            'profession1Reason': 'Tertarik dengan arsitektur data dan logika server.',
            'priorityProfession': 'Backend Developer',
            'actionStep1': 'Mempelajari Django ORM.',
            'actionStep2': 'Membuat CRUD API sederhana.',
            'additional_notes': 'Mohon reviewnya Pak Agung.',
        }
        response = self.client.post(reverse('pembelajaran:submit_lkpd', kwargs={'slug': modul2.slug}), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'LKPD OR-02 &amp; Link Google Drive Evidence berhasil dikirim!')

        sub = UserSubmission.objects.filter(user=self.student, modul=modul2, submission_type='lkpd').first()
        self.assertIsNotNone(sub)
        self.assertEqual(sub.drive_url, 'https://drive.google.com/drive/folders/test_evidence_modul2')
        self.assertEqual(sub.form_data['profession1Name'], 'Backend Developer')
        self.assertEqual(sub.form_data['priorityProfession'], 'Backend Developer')
        self.assertEqual(sub.form_data['schema_answers']['profession1Tools'], 'Python, Django, PostgreSQL')


