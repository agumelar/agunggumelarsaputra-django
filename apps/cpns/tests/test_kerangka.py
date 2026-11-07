from django.template.loader import render_to_string
from django.test import TestCase

HOST_CPNS = 'cpns.agunggumelarsaputra.com'
HOST_UTAMA = 'localhost'


class KerangkaTampilanTests(TestCase):
    def test_judul_tab_cpns(self):
        resp = self.client.get('/', HTTP_HOST=HOST_CPNS)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(' | CPNS Hub</title>', resp.content.decode())

    def test_halaman_utama_tetap_rpl(self):
        resp = self.client.get('/', HTTP_HOST=HOST_UTAMA)
        self.assertIn('| RPL SMKN 1 Rongga', resp.content.decode())

    def test_bar_skor_kurang(self):
        html = render_to_string('cpns/komponen/bar_skor.html', {
            'subtes': 'TIU', 'skor': 75, 'maks': 175, 'ambang': 80, 'lulus': False,
        })
        self.assertIn('Kurang 5 (ambang 80)', html)

    def test_bar_skor_lolos(self):
        html = render_to_string('cpns/komponen/bar_skor.html', {
            'subtes': 'TWK', 'skor': 70, 'maks': 150, 'ambang': 65, 'lulus': True,
        })
        self.assertIn('Lolos (ambang 65)', html)

    def test_bar_skor_tanpa_ambang(self):
        html = render_to_string('cpns/komponen/bar_skor.html', {
            'subtes': 'TWK', 'skor': 70, 'maks': 150, 'ambang': 0, 'lulus': True,
        })
        self.assertIn('Selesai', html)
        self.assertNotIn('ambang', html)
