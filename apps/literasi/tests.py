import json
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
        # 33 words sample moral message
        self.valid_moral = "Amanat penting dari bacaan ini adalah kejujuran dan ketekunan dalam menulis kode program. Seorang pengembang perangkat lunak profesional harus senantiasa memperhatikan kualitas, arsitektur, dan kemudahan pemeliharaan sistem demi kemaslahatan pengguna dan masyarakat."

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
            'moral_message': self.valid_moral,
        }
        response = self.client.post(reverse('literasi:submit_literasi'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Syarat minimal laporan RESIK adalah 100 kata')
        self.assertEqual(LiterasiReport.objects.count(), 0)

    def test_submit_literasi_fails_under_30_words_moral(self):
        """Test submitting report with less than 30 words moral message fails validation."""
        self.client.login(username='siswa_fauzi', password='password123')
        data = {
            'week_number': 1,
            'report_date': '2026-08-26',
            'book_title': 'Clean Code',
            'author': 'Robert C. Martin',
            'source_type': 'Buku Fisik',
            'summary': self.valid_summary,
            'moral_message': 'Terlalu pendek satu baris.',
        }
        response = self.client.post(reverse('literasi:submit_literasi'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Syarat minimal adalah 30 kata')
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
            'moral_message': self.valid_moral,
            'check_tata_bahasa': 'on',
            'check_tanda_baca': 'on',
            'check_kalimat_efektif': 'on',
            'check_bahasa_baku': 'on',
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
        self.assertTrue(report.self_checklist.get('tata_bahasa'))

    def test_submit_peer_review_success_and_awards_xp(self):
        """Test peer review from classmate awards +5 XP for reviewer."""
        report = LiterasiReport.objects.create(
            user=self.student1,
            week_number=1,
            book_title='Clean Architecture',
            author='Uncle Bob',
            source_type='Buku Fisik',
            summary=self.valid_summary,
            moral_message=self.valid_moral,
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
            moral_message=self.valid_moral,
            word_count=105
        )

        self.client.login(username='siswa_fauzi', password='password123')
        data = {'rating': 5, 'comment': 'Review diri sendiri'}
        response = self.client.post(reverse('literasi:submit_peer_review', kwargs={'report_id': report.id}), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Anda tidak dapat mereview laporan Anda sendiri')

    def test_grade_literasi_by_teacher_9_aspects(self):
        """Test teacher evaluating student report using 9-aspect rubric formula."""
        report = LiterasiReport.objects.create(
            user=self.student1,
            week_number=1,
            book_title='Clean Architecture',
            author='Uncle Bob',
            source_type='Buku Fisik',
            summary=self.valid_summary,
            moral_message=self.valid_moral,
            word_count=105,
            status='submitted'
        )

        self.client.login(username='guru_agung', password='password123')

        payload = {
            'reportId': report.id,
            'w1': 4, 'w2': 4, 'w3': 3, 'w4': 4, # Total writing = 15/16
            'p1': 4, 'p2': 4, 'p3': 3, 'p4': 4, 'p5': 4, # Total presentation = 19/20
            # Total score = 34 / 36 * 100 = 94
            'teacherFeedback': 'Analisis buku dan pesan moral sangat tajam!'
        }
        response = self.client.post(
            reverse('literasi:grade_literasi'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['writing_score'], 15)
        self.assertEqual(data['presentation_score'], 19)
        self.assertEqual(data['final_score'], 94)

        report.refresh_from_db()
        self.assertEqual(report.status, 'graded')
        self.assertEqual(report.writing_score, 15)
        self.assertEqual(report.presentation_score, 19)
        self.assertEqual(report.final_score, 94.0)
        self.assertEqual(report.graded_by, self.teacher)

    def test_grade_literasi_by_student_forbidden(self):
        """Test student cannot access teacher grading endpoint."""
        report = LiterasiReport.objects.create(
            user=self.student1,
            week_number=1,
            book_title='Clean Architecture',
            author='Uncle Bob',
            source_type='Buku Fisik',
            summary=self.valid_summary,
            moral_message=self.valid_moral,
            word_count=105,
            status='submitted'
        )
        self.client.login(username='siswa_budi', password='password123')
        payload = {'reportId': report.id, 'w1': 4, 'w2': 4, 'w3': 4, 'w4': 4, 'p1': 4, 'p2': 4, 'p3': 4, 'p4': 4, 'p5': 4}
        response = self.client.post(
            reverse('literasi:grade_literasi'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    def test_export_rekap_by_teacher(self):
        """Test teacher can export literasi recap to CSV."""
        LiterasiReport.objects.create(
            user=self.student1,
            week_number=1,
            book_title='Clean Architecture',
            author='Uncle Bob',
            source_type='Buku Fisik',
            summary=self.valid_summary,
            moral_message=self.valid_moral,
            word_count=105,
            status='graded',
            final_score=94.0
        )
        self.client.login(username='guru_agung', password='password123')
        response = self.client.get(reverse('literasi:export_rekap'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8-sig')
        self.assertIn('Rekap_Rabu_Literasi_RESIK_SMKN1Rongga.csv', response['Content-Disposition'])
        self.assertContains(response, 'Ahmad Fauzi')
        self.assertContains(response, 'Clean Architecture')

    def test_export_rekap_by_student_forbidden(self):
        """Test student cannot export literasi recap."""
        self.client.login(username='siswa_fauzi', password='password123')
        response = self.client.get(reverse('literasi:export_rekap'))
        self.assertEqual(response.status_code, 403)

