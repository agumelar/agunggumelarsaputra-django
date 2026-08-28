from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.literasi.models import LiterasiReport, LiterasiPeerReview

User = get_user_model()


class LiterasiModuleTestCase(TestCase):
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

        # Create Student 1 (Author)
        self.student1 = User.objects.create_user(
            username='siswa_fauzi',
            email='fauzi@smkn1rongga.sch.id',
            password='password123',
            first_name='Ahmad',
            last_name='Fauzi',
            role=User.ROLE_SISWA,
            kelas='10 RPL 1',
            xp=50
        )

        # Create Student 2 (Reviewer)
        self.student2 = User.objects.create_user(
            username='siswa_budi',
            email='budi@smkn1rongga.sch.id',
            password='password123',
            first_name='Budi',
            last_name='Santoso',
            role=User.ROLE_SISWA,
            kelas='10 RPL 1',
            xp=30
        )

        # 105 words sample summary text
        self.valid_summary = " ".join(["kata"] * 105)

    def test_literasi_hub_view(self):
        """Test literasi_hub_view returns 200 and renders RESIK branding."""
        response = self.client.get(reverse('literasi:literasi_hub'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rabu Literasi (RESIK)')
        self.assertContains(response, '100 Kata')

    def test_submit_literasi_fails_under_100_words(self):
        """Test submitting report with less than 100 words fails validation."""
        self.client.login(username='siswa_fauzi', password='password123')
        data = {
            'week_number': 1,
            'report_date': '2026-08-26',
            'book_title': 'Clean Code',
            'author': 'Robert C. Martin',
            'source_type': 'Buku Fisik',
            'summary': 'Ini ringkasan yang terlalu pendek hanya beberapa kata saja.',
            'moral_message': 'Pentingnya menulis kode bersih.',
        }
        response = self.client.post(reverse('literasi:submit_literasi'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Syarat minimal laporan RESIK adalah 100 kata')
        self.assertEqual(LiterasiReport.objects.count(), 0)

    def test_submit_literasi_success_and_awards_xp(self):
        """Test submitting valid report creates LiterasiReport and awards +35 XP."""
        self.client.login(username='siswa_fauzi', password='password123')
        initial_xp = self.student1.xp

        data = {
            'week_number': 1,
            'report_date': '2026-08-26',
            'book_title': 'Clean Architecture',
            'author': 'Uncle Bob',
            'publisher': 'Prentice Hall',
            'city': 'Boston',
            'year': '2018',
            'page_count': '1-50',
            'source_type': 'Buku Fisik',
            'summary': self.valid_summary,
            'moral_message': 'Arsitektur perangkat lunak yang bersih memisahkan bisnis logic dari framework.',
        }
        response = self.client.post(reverse('literasi:submit_literasi'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'berhasil dikirim!')
        self.assertContains(response, '+35 XP')

        self.student1.refresh_from_db()
        self.assertEqual(self.student1.xp, initial_xp + 35)

        report = LiterasiReport.objects.get(user=self.student1)
        self.assertEqual(report.book_title, 'Clean Architecture')
        self.assertEqual(report.word_count, 105)
        self.assertEqual(report.status, 'submitted')

    def test_submit_peer_review_success_and_awards_xp(self):
        """Test peer review from classmate awards +5 XP for reviewer."""
        report = LiterasiReport.objects.create(
            user=self.student1,
            week_number=1,
            book_title='Clean Architecture',
            author='Uncle Bob',
            source_type='Buku Fisik',
            summary=self.valid_summary,
            moral_message='Pemisahan domain layer.',
            word_count=105,
            status='submitted'
        )

        self.client.login(username='siswa_budi', password='password123')
        initial_xp = self.student2.xp

        data = {
            'rating': 5,
            'comment': 'Rangkuman sangat terstruktur dan jelas!',
        }
        response = self.client.post(reverse('literasi:submit_peer_review', kwargs={'report_id': report.id}), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Terima kasih!')
        self.assertContains(response, '+5 XP')

        self.student2.refresh_from_db()
        self.assertEqual(self.student2.xp, initial_xp + 5)

        review = LiterasiPeerReview.objects.get(report=report, reviewer=self.student2)
        self.assertEqual(review.rating, 5)

    def test_student_cannot_peer_review_own_report(self):
        """Test student cannot review their own report."""
        report = LiterasiReport.objects.create(
            user=self.student1,
            week_number=1,
            book_title='Clean Architecture',
            author='Uncle Bob',
            source_type='Buku Fisik',
            summary=self.valid_summary,
            moral_message='Pemisahan domain layer.',
            word_count=105
        )

        self.client.login(username='siswa_fauzi', password='password123')
        data = {'rating': 5, 'comment': 'Review diri sendiri'}
        response = self.client.post(reverse('literasi:submit_peer_review', kwargs={'report_id': report.id}), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Anda tidak dapat mereview laporan Anda sendiri')

    def test_teacher_grading_literasi(self):
        """Test teacher can view and grade student literasi report."""
        report = LiterasiReport.objects.create(
            user=self.student1,
            week_number=1,
            book_title='Clean Architecture',
            author='Uncle Bob',
            source_type='Buku Fisik',
            summary=self.valid_summary,
            moral_message='Pemisahan domain layer.',
            word_count=105,
            status='submitted'
        )

        self.client.login(username='guru_agung', password='password123')
        
        # Access list
        response_list = self.client.get(reverse('admin_panel:literasi_list'))
        self.assertEqual(response_list.status_code, 200)
        self.assertContains(response_list, 'Clean Architecture')

        # Grade report
        grade_data = {
            'writing_score': 90,
            'presentation_score': 88,
            'teacher_feedback': 'Rangkuman RESIK sangat komprehensif. Pertahankan konsistensinya!',
        }
        response_grade = self.client.post(reverse('admin_panel:literasi_grade', kwargs={'report_id': report.id}), grade_data)
        self.assertRedirects(response_grade, reverse('admin_panel:literasi_list'))

        report.refresh_from_db()
        self.assertEqual(report.status, 'graded')
        self.assertEqual(report.writing_score, 90)
        self.assertEqual(report.presentation_score, 88)
        self.assertEqual(report.final_score, 89.0)
        self.assertEqual(report.graded_by, self.teacher)
