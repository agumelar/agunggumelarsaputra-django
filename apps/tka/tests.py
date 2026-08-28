import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.tka.models import TkaPackage, TkaQuestion, TkaAttempt

User = get_user_model()


class TkaModuleTestCase(TestCase):
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

        # Create TKA Package
        self.package = TkaPackage.objects.create(
            kode='TKA-01',
            judul='Pertemuan 1: Algoritma & Logika Pemrograman',
            slug='tka-01-algoritma-logika',
            kategori='Drilling TKA PPLG',
            level='Lanjutan',
            durasi_menit=60,
            passing_grade=75,
            deskripsi='Review dan latihan soal algoritma dasar dan flowchart.',
            content_materi='## The Core of Algorithm\n\nAlgoritma adalah langkah logis.',
            teacher_tip='Fokus pada tracing variabel nested loop.',
            urutan=1,
            xp_base=25,
            is_published=True
        )

        # Create Questions for Package
        self.q1 = TkaQuestion.objects.create(
            package=self.package,
            urutan=1,
            question_text='Langkah sistematis dan logis dalam menyelesaikan masalah disebut...',
            option_a='Program',
            option_b='Algoritma',
            option_c='Flowchart',
            option_d='Pseudocode',
            option_e='Sintaksis',
            correct_answer='B',
            explanation='Algoritma adalah urutan langkah logis.',
            category='Algoritma & Logika'
        )

        self.q2 = TkaQuestion.objects.create(
            package=self.package,
            urutan=2,
            question_text='Tipe data untuk menyimpan nilai bilangan bulat adalah...',
            option_a='Float',
            option_b='String',
            option_c='Integer',
            option_d='Boolean',
            option_e='Double',
            correct_answer='C',
            explanation='Integer adalah tipe data bilangan bulat.',
            category='Algoritma & Logika'
        )

    def test_tka_list_view(self):
        """Test tka_list_view returns 200 and displays package."""
        response = self.client.get(reverse('tka:tka_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TKA-01')
        self.assertContains(response, 'Algoritma')

    def test_tka_detail_view(self):
        """Test tka_detail_view renders bedah materi and package details for logged in student."""
        self.client.login(username='siswa_fauzi', password='password123')
        response = self.client.get(reverse('tka:tka_detail', kwargs={'slug': self.package.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TKA-01')
        self.assertContains(response, 'Passing Grade: 75%')
        self.assertContains(response, 'Mulai Simulasi CBT Sekarang')

    def test_tka_exam_view_requires_login(self):
        """Test accessing exam without login redirects to login."""
        response = self.client.get(reverse('tka:tka_exam', kwargs={'slug': self.package.slug}))
        self.assertEqual(response.status_code, 302)

    def test_tka_exam_view_authenticated(self):
        """Test logged in student can access CBT exam interface."""
        self.client.login(username='siswa_fauzi', password='password123')
        response = self.client.get(reverse('tka:tka_exam', kwargs={'slug': self.package.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cbtSimulator')

    def test_tka_submit_and_auto_scoring(self):
        """Test auto-scoring calculation, bonus XP, and attempt creation."""
        self.client.login(username='siswa_fauzi', password='password123')
        initial_xp = self.student.xp

        # Student answers Q1 correctly ('B') and Q2 incorrectly ('A') -> 1/2 = 50%
        answers_payload = {
            str(self.q1.id): 'B',
            str(self.q2.id): 'A',
        }

        data = {
            'answers_payload': json.dumps(answers_payload),
            'time_spent_seconds': 120,
        }

        response = self.client.post(reverse('tka:tka_submit', kwargs={'slug': self.package.slug}), data)
        self.assertEqual(response.status_code, 302)

        # Verify attempt record
        attempt = TkaAttempt.objects.get(user=self.student, package=self.package)
        self.assertEqual(attempt.score, 50.0)
        self.assertEqual(attempt.correct_answers, 1)
        self.assertEqual(attempt.wrong_answers, 1)
        self.assertFalse(attempt.is_passed)  # 50% < 75%

        # Bonus XP: xp_base(25) + round((50/100)*50) = 25 + 25 = 50 XP
        self.assertEqual(attempt.xp_earned, 50)

        self.student.refresh_from_db()
        self.assertEqual(self.student.xp, initial_xp + 50)

    def test_tka_submit_passing_score(self):
        """Test student scoring 100% passes the passing grade."""
        self.client.login(username='siswa_fauzi', password='password123')

        answers_payload = {
            str(self.q1.id): 'B',
            str(self.q2.id): 'C',
        }

        data = {
            'answers_payload': json.dumps(answers_payload),
            'time_spent_seconds': 90,
        }

        response = self.client.post(reverse('tka:tka_submit', kwargs={'slug': self.package.slug}), data)
        self.assertEqual(response.status_code, 302)

        attempt = TkaAttempt.objects.get(user=self.student, package=self.package)
        self.assertEqual(attempt.score, 100.0)
        self.assertTrue(attempt.is_passed)

    def test_tka_result_view(self):
        """Test result review displays score and explanation."""
        attempt = TkaAttempt.objects.create(
            user=self.student,
            package=self.package,
            score=100.0,
            total_questions=2,
            correct_answers=2,
            wrong_answers=0,
            user_answers={str(self.q1.id): 'B', str(self.q2.id): 'C'},
            xp_earned=75,
            is_passed=True,
            time_spent_seconds=90
        )

        self.client.login(username='siswa_fauzi', password='password123')
        response = self.client.get(reverse('tka:tka_result', kwargs={'slug': self.package.slug, 'attempt_id': attempt.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'LULUS KKM')
        self.assertContains(response, 'Algoritma adalah urutan langkah logis.')

    def test_teacher_can_view_tka_results(self):
        """Test teacher can access TKA results monitoring dashboard."""
        self.client.login(username='guru_agung', password='password123')
        response = self.client.get(reverse('admin_panel:tka_results'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hasil Simulasi CBT TKA PPLG Siswa')
