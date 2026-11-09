from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()
CPNS_HOST = 'cpns.agunggumelarsaputra.com'

# (alamat lama tanpa prefiks, nama tujuan)
ALAMAT_LAMA = [
    ('packages/', 'cpns:beranda'),
    ('packages/skd-bkn-01/', 'cpns:beranda'),
    ('exam/skd-bkn-01/', 'cpns:dasbor'),
    ('exam/skd-bkn-01/submit/', 'cpns:dasbor'),
    ('result/skd-bkn-01/7/', 'cpns:riwayat'),
]

HOSTS = [
    # (label, awalan path, kwargs request, urlconf untuk reverse)
    ('subdomain', '/', {'HTTP_HOST': CPNS_HOST}, 'config.cpns_urls'),
    ('domain utama', '/cpns/', {}, None),
]


class AlamatLamaTest(TestCase):
    def test_alamat_lama_dialihkan_permanen_di_kedua_host(self):
        for label, awalan, extra, urlconf in HOSTS:
            for lama, tujuan in ALAMAT_LAMA:
                with self.subTest(host=label, alamat=lama):
                    response = self.client.get(awalan + lama, **extra)
                    self.assertEqual(response.status_code, 301)
                    self.assertEqual(response['Location'], reverse(tujuan, urlconf=urlconf))

    def test_query_string_tidak_ikut(self):
        response = self.client.get('/exam/skd-bkn-01/?x=1', HTTP_HOST=CPNS_HOST)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], '/dasbor/')

    def test_tujuan_tidak_mengalihkan_lagi(self):
        for label, awalan, extra, urlconf in HOSTS:
            for lama, tujuan in ALAMAT_LAMA:
                with self.subTest(host=label, alamat=lama):
                    response = self.client.get(awalan + lama, **extra)
                    akhir = self.client.get(response['Location'], **extra)
                    self.assertIn(akhir.status_code, (200, 302))
                    if akhir.status_code == 302:
                        self.assertIn('masuk', akhir['Location'])

    def test_peserta_login_di_host_cpns_langsung_301(self):
        peserta = User.objects.create_user(
            username='peserta_lama', email='lama@example.com',
            password='Password123!', role=User.ROLE_PESERTA,
        )
        self.client.force_login(peserta)
        for lama, tujuan in ALAMAT_LAMA:
            with self.subTest(alamat=lama):
                response = self.client.get('/' + lama, HTTP_HOST=CPNS_HOST)
                self.assertEqual(response.status_code, 301)
                self.assertEqual(
                    response['Location'], reverse(tujuan, urlconf='config.cpns_urls'))
