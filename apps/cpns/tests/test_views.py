import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.cpns.models import CpnsPackage, CpnsQuestion, CpnsAttempt

User = get_user_model()


class CpnsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='peserta_cpns',
            email='peserta@example.com',
            password='Password123!',
            role='student'
        )

        self.pkg = CpnsPackage.objects.create(
            kode='SKD-BKN-TEST-VIEW',
            judul='Paket Simulasi SKD Test View',
            slug='paket-simulasi-skd-test-view',
            tipe_ujian='SKD',
            durasi_menit=100,
            passing_grade_twk=65,
            passing_grade_tiu=80,
            passing_grade_tkp=166,
            is_published=True
        )

        self.q1 = CpnsQuestion.objects.create(
            package=self.pkg,
            subtes='TWK',
            subtopik='Pancasila',
            urutan=1,
            pertanyaan='Pertanyaan TWK 1',
            opsi_a='A1', opsi_b='B1', opsi_c='C1', opsi_d='D1', opsi_e='E1',
            kunci_jawaban='A',
            bedah_konsep='Konsep TWK 1',
            alasan_pengecoh='Pengecoh TWK 1',
            tips_cepat='Tips TWK 1'
        )

        self.q2 = CpnsQuestion.objects.create(
            package=self.pkg,
            subtes='TKP',
            subtopik='Pelayanan Publik',
            urutan=2,
            pertanyaan='Pertanyaan TKP 2',
            opsi_a='A2', opsi_b='B2', opsi_c='C2', opsi_d='D2', opsi_e='E2',
            kunci_jawaban='C',
            bobot_tkp={'A': 1, 'B': 2, 'C': 5, 'D': 3, 'E': 4},
            bedah_konsep='Konsep TKP 2',
            alasan_pengecoh='Pengecoh TKP 2',
            tips_cepat='Tips TKP 2'
        )

    def test_landing_and_package_list(self):
        """Uji view landing dan katalog paket soal."""
        res_landing = self.client.get(reverse('cpns:landing'))
        self.assertEqual(res_landing.status_code, 200)

        res_list = self.client.get(reverse('cpns:package_list'))
        self.assertEqual(res_list.status_code, 200)
        self.assertContains(res_list, self.pkg.judul)

    def test_package_detail(self):
        """Uji halaman pengantar paket ujian."""
        url = reverse('cpns:package_detail', kwargs={'slug': self.pkg.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.pkg.judul)

    def test_cbt_exam_room(self):
        """Uji ruang ujian CAT interaktif."""
        url = reverse('cpns:cbt_exam', kwargs={'slug': self.pkg.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('questions_json', response.context)
        self.assertEqual(response.context['total_questions'], 2)

    def test_cbt_submit_and_redirect_to_result(self):
        """Uji POST submit jawaban dan kalkulasi skor di view controller."""
        self.client.force_login(self.user)
        submit_url = reverse('cpns:cbt_submit', kwargs={'slug': self.pkg.slug})
        
        payload = {
            str(self.q1.id): 'A',  # TWK Benar (5 poin)
            str(self.q2.id): 'C',  # TKP Opsi C (5 poin)
        }

        data = {
            'answers_payload': json.dumps(payload),
            'time_spent_seconds': 1500,
            'mode': 'SIMULASI_CAT'
        }

        response = self.client.post(submit_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect ke result

        # Pastikan attempt tercipta
        attempt = CpnsAttempt.objects.filter(package=self.pkg, user=self.user).first()
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.skor_twk, 5)
        self.assertEqual(attempt.skor_tkp, 5)

        # Akses halaman result
        result_url = reverse('cpns:cbt_result', kwargs={'slug': self.pkg.slug, 'attempt_id': attempt.id})
        res_result = self.client.get(result_url)
        self.assertEqual(res_result.status_code, 200)
        self.assertContains(res_result, 'Konsep TWK 1')
