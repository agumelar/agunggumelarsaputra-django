import json
import re

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.cpns.models import CpnsAttempt, CpnsPackage, CpnsQuestion

User = get_user_model()
CPNS_HOST = 'cpns.agunggumelarsaputra.com'


class CpnsSubdomainAccountPagesTest(TestCase):
    """Halaman akun memakai navbar utama; di subdomain cpns tidak boleh 500."""

    def test_login_page_renders_on_cpns_subdomain(self):
        response = self.client.get('/accounts/login/', HTTP_HOST=CPNS_HOST)
        self.assertEqual(response.status_code, 200)

    def test_register_page_renders_on_cpns_subdomain(self):
        response = self.client.get('/accounts/register/', HTTP_HOST=CPNS_HOST)
        self.assertEqual(response.status_code, 200)


class LoginNextRedirectTest(TestCase):
    def setUp(self):
        User.objects.create_user(
            username='peserta_next', email='next@example.com',
            password='Password123!', role='student',
        )

    def _login(self, next_url):
        return self.client.post(
            f'/accounts/login/?next={next_url}',
            {'identifier': 'peserta_next', 'password': 'Password123!'},
            HTTP_HOST=CPNS_HOST,
        )

    def test_next_to_same_site_path_is_followed(self):
        response = self._login('/packages/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/packages/')

    def test_next_to_external_site_is_ignored(self):
        response = self._login('https://evil.example.com/')
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('evil.example.com', response['Location'])


class CpnsSubmitValidationTest(TestCase):
    def setUp(self):
        self.pkg = CpnsPackage.objects.create(
            kode='SKD-VALID-01', judul='Paket Validasi', slug='paket-validasi',
            tipe_ujian='SKD', durasi_menit=100, is_published=True,
        )
        self.q_twk = CpnsQuestion.objects.create(
            package=self.pkg, subtes='TWK', urutan=1, pertanyaan='Soal TWK',
            opsi_a='a', opsi_b='b', opsi_c='c', opsi_d='d', opsi_e='e',
            kunci_jawaban='A',
        )
        self.url = f'/exam/{self.pkg.slug}/submit/'

    def _submit(self, answers_payload='{}', time_spent='10', mode='SIMULASI_CAT'):
        return self.client.post(self.url, {
            'answers_payload': answers_payload,
            'time_spent_seconds': time_spent,
            'mode': mode,
        }, HTTP_HOST=CPNS_HOST)

    def test_answers_payload_that_is_not_an_object_is_rejected(self):
        response = self._submit(answers_payload='[]')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(CpnsAttempt.objects.count(), 0)

    def test_non_numeric_time_is_rejected(self):
        response = self._submit(time_spent='abc')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(CpnsAttempt.objects.count(), 0)

    def test_negative_time_is_rejected(self):
        response = self._submit(time_spent='-5')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(CpnsAttempt.objects.count(), 0)

    def test_unknown_mode_is_rejected(self):
        response = self._submit(mode='XYZ')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(CpnsAttempt.objects.count(), 0)

    def test_invalid_answer_values_are_dropped_not_crashing(self):
        payload = json.dumps({str(self.q_twk.id): 5, '999999': 'A'})
        response = self._submit(answers_payload=payload)
        self.assertEqual(response.status_code, 302)
        attempt = CpnsAttempt.objects.get()
        self.assertEqual(attempt.jawaban_peserta, {})
        self.assertEqual(attempt.skor_twk, 0)

    def test_lowercase_answer_is_accepted(self):
        payload = json.dumps({str(self.q_twk.id): 'a'})
        response = self._submit(answers_payload=payload)
        self.assertEqual(response.status_code, 302)
        attempt = CpnsAttempt.objects.get()
        self.assertEqual(attempt.jawaban_peserta, {str(self.q_twk.id): 'A'})
        self.assertEqual(attempt.skor_twk, 5)


class CpnsExamModeTest(TestCase):
    def setUp(self):
        self.pkg = CpnsPackage.objects.create(
            kode='SKD-MODE-01', judul='Paket Mode', slug='paket-mode',
            tipe_ujian='SKD', durasi_menit=100, is_published=True,
        )
        CpnsQuestion.objects.create(
            package=self.pkg, subtes='TWK', urutan=1, pertanyaan='Soal',
            opsi_a='a', opsi_b='b', opsi_c='c', opsi_d='d', opsi_e='e',
            kunci_jawaban='A',
        )

    def _exam(self, mode):
        return self.client.get(f'/exam/{self.pkg.slug}/?mode={mode}', HTTP_HOST=CPNS_HOST)

    def test_unknown_mode_falls_back_to_simulation(self):
        response = self._exam('XYZ')
        self.assertEqual(response.context['mode'], 'SIMULASI_CAT')
        self.assertEqual(response.context['duration_seconds'], 100 * 60)

    def test_drilling_mode_badge_says_drilling(self):
        html = self._exam('DRILLING_BEBAS').content.decode()
        self.assertRegex(html, r'>\s*Drilling Bebas\s*<')
        self.assertIsNone(re.search(r'>\s*Simulasi CAT\s*<', html))

    def test_simulation_mode_badge_says_simulation(self):
        html = self._exam('SIMULASI_CAT').content.decode()
        self.assertRegex(html, r'>\s*Simulasi CAT\s*<')
