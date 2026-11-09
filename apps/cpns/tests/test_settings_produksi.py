"""Pengaturan produksi harus gagal-tertutup.

Settings dimuat di subproses supaya tes tidak mengubah settings proses ini.
Variabel yang dikosongkan ('') dianggap hilang. load_dotenv tidak menimpa
variabel yang sudah ada, jadi .env lokal tidak ikut campur.
"""
import json
import os
import re
import string
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase

BASE_DIR = Path(__file__).resolve().parents[3]
KUNCI_UJI = (string.ascii_letters + string.digits) * 2
SANDI_UJI = 'uji' + string.digits

VARIABEL = [
    'DJANGO_SECRET_KEY', 'DATABASE_URL', 'DB_PASSWORD', 'DB_NAME', 'DB_USER',
    'DB_HOST', 'ALLOWED_HOSTS', 'CSRF_TRUSTED_ORIGINS', 'SESSION_COOKIE_SECURE',
    'CSRF_COOKIE_SECURE', 'SECURE_HSTS_SECONDS', 'SECURE_SSL_REDIRECT', 'DEBUG',
    'CPNS_URL', 'GURU_EMAILS', 'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET',
]

KODE = (
    "import json, django\n"
    "from django.conf import settings\n"
    "print(json.dumps({'hosts': settings.ALLOWED_HOSTS,"
    " 'csrf': settings.CSRF_TRUSTED_ORIGINS,"
    " 'sesi': settings.SESSION_COOKIE_SECURE,"
    " 'csrf_cookie': settings.CSRF_COOKIE_SECURE,"
    " 'hsts': settings.SECURE_HSTS_SECONDS,"
    " 'hsts_sub': settings.SECURE_HSTS_INCLUDE_SUBDOMAINS,"
    " 'hsts_preload': settings.SECURE_HSTS_PRELOAD,"
    " 'ssl_redirect': settings.SECURE_SSL_REDIRECT,"
    " 'db_pass': bool(settings.DATABASES['default']['PASSWORD'])}))\n"
)


def jalankan(argumen, **env_tambahan):
    env = {k: v for k, v in os.environ.items() if k not in VARIABEL}
    env.update({k: '' for k in VARIABEL})
    env['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'
    env['DJANGO_SECRET_KEY'] = KUNCI_UJI
    env['DB_PASSWORD'] = SANDI_UJI
    env.update(env_tambahan)
    return subprocess.run(
        [sys.executable, *argumen], cwd=BASE_DIR, env=env,
        capture_output=True, text=True, timeout=120,
    )


def muat(**env_tambahan):
    return jalankan(['-c', KODE], **env_tambahan)


class SettingsProduksiTest(SimpleTestCase):
    def test_tanpa_secret_key_gagal(self):
        hasil = muat(DJANGO_SECRET_KEY='')
        self.assertNotEqual(hasil.returncode, 0)
        self.assertIn('DJANGO_SECRET_KEY wajib diisi di .env produksi.', hasil.stderr)

    def test_tanpa_password_db_gagal(self):
        hasil = muat(DB_PASSWORD='', DATABASE_URL='')
        self.assertNotEqual(hasil.returncode, 0)
        self.assertIn('DB_PASSWORD atau DATABASE_URL wajib diisi.', hasil.stderr)

    def test_database_url_tanpa_password_gagal(self):
        hasil = muat(DB_PASSWORD='', DATABASE_URL='postgres://pengguna@db:5432/nama')
        self.assertNotEqual(hasil.returncode, 0)
        self.assertIn('DB_PASSWORD atau DATABASE_URL wajib diisi.', hasil.stderr)

    def test_database_url_berpassword_diterima(self):
        hasil = muat(DB_PASSWORD='', DATABASE_URL='postgres://pengguna:rahasia@db:5432/nama')
        self.assertEqual(hasil.returncode, 0, hasil.stderr)
        self.assertTrue(json.loads(hasil.stdout)['db_pass'])

    def test_allowed_hosts_bintang_ditolak(self):
        for nilai in ('*', 'agunggumelarsaputra.com, *'):
            with self.subTest(nilai=nilai):
                hasil = muat(ALLOWED_HOSTS=nilai)
                self.assertNotEqual(hasil.returncode, 0)
                self.assertIn('ImproperlyConfigured', hasil.stderr)
                self.assertIn('ALLOWED_HOSTS', hasil.stderr)

    def test_allowed_hosts_bisa_diganti_lewat_env(self):
        hasil = muat(ALLOWED_HOSTS='contoh.test, lain.test')
        self.assertEqual(hasil.returncode, 0, hasil.stderr)
        self.assertEqual(json.loads(hasil.stdout)['hosts'], ['contoh.test', 'lain.test'])

    def test_bawaan_aman(self):
        hasil = muat()
        self.assertEqual(hasil.returncode, 0, hasil.stderr)
        data = json.loads(hasil.stdout)
        domain = ['agunggumelarsaputra.com', 'www.agunggumelarsaputra.com',
                  'cpns.agunggumelarsaputra.com']
        self.assertEqual(data['hosts'], domain)
        self.assertEqual(data['csrf'], ['https://' + d for d in domain])
        self.assertIs(data['sesi'], True)
        self.assertIs(data['csrf_cookie'], True)
        self.assertEqual(data['hsts'], 3600)
        self.assertIs(data['hsts_sub'], False)
        self.assertIs(data['hsts_preload'], False)
        self.assertIs(data['ssl_redirect'], False)

    def test_hsts_bisa_diatur_lewat_env(self):
        hasil = muat(SECURE_HSTS_SECONDS='86400')
        self.assertEqual(json.loads(hasil.stdout)['hsts'], 86400)

    def test_check_deploy_bersih(self):
        hasil = jalankan(
            ['manage.py', 'check', '--deploy', '--fail-level', 'ERROR'],
            CPNS_URL='https://cpns.agunggumelarsaputra.com/',
        )
        self.assertEqual(hasil.returncode, 0, hasil.stdout + hasil.stderr)


class ComposeTanpaRahasiaTest(SimpleTestCase):
    def setUp(self):
        self.teks = (BASE_DIR / 'docker-compose.yml').read_text(encoding='utf-8')

    def test_compose_tanpa_rahasia(self):
        for baris in self.teks.splitlines():
            if 'PASSWORD' in baris and '=' in baris:
                nilai = baris.split('=', 1)[1].strip()
                self.assertTrue(
                    nilai == '' or nilai.startswith('${'),
                    f'Nilai literal pada baris: {baris.split("=")[0].strip()}',
                )
        self.assertNotIn('ALLOWED_HOSTS=*', self.teks)
        self.assertIsNone(re.search(r'(SESSION|CSRF)_COOKIE_SECURE=False', self.teks))

    def test_entrypoint_tanpa_sandi_bawaan(self):
        teks = (BASE_DIR / 'scripts' / 'entrypoint.sh').read_text(encoding='utf-8')
        self.assertNotRegex(teks, r"DB_PASSWORD',\s*'[^']")

    def test_env_contoh_hanya_placeholder(self):
        teks = (BASE_DIR / '.env.example').read_text(encoding='utf-8')
        for nama in ('DJANGO_SECRET_KEY', 'DB_PASSWORD', 'POSTGRES_PASSWORD',
                     'GOOGLE_CLIENT_SECRET'):
            self.assertRegex(teks, rf'(?m)^{nama}=\[ISI\]$')
