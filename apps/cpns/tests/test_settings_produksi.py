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
    'DB_PORT', 'STATIC_ROOT', 'MEDIA_ROOT',
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

    def test_secret_key_tidak_aman_ditolak(self):
        pesan = 'DJANGO_SECRET_KEY tidak aman. Buat kunci acak baru minimal 50 karakter.'
        kasus = {
            'bawaan_django': 'django-insecure-' + 'x' * 60,
            'pendek': 'x' * 49,
        }
        for nama, nilai in kasus.items():
            with self.subTest(kasus=nama):
                hasil = muat(DJANGO_SECRET_KEY=nilai)
                self.assertNotEqual(hasil.returncode, 0)
                self.assertIn(pesan, hasil.stderr)

    def test_secret_key_50_karakter_diterima(self):
        hasil = muat(DJANGO_SECRET_KEY='x' * 50)
        self.assertEqual(hasil.returncode, 0, hasil.stderr)

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

    def test_nilai_isi_ditolak_untuk_setiap_variabel(self):
        for nama in VARIABEL:
            with self.subTest(nama=nama):
                hasil = muat(**{nama: '[ISI]'})
                self.assertNotEqual(hasil.returncode, 0)
                self.assertIn('ImproperlyConfigured', hasil.stderr)
                self.assertIn(
                    f'{nama} masih berisi [ISI]. Isi nilainya atau hapus barisnya.',
                    hasil.stderr,
                )

    def test_isi_di_tengah_nilai_juga_ditolak(self):
        hasil = muat(DJANGO_SECRET_KEY='[ISI]' + 'x' * 60)
        self.assertNotEqual(hasil.returncode, 0)
        self.assertIn('DJANGO_SECRET_KEY masih berisi [ISI].', hasil.stderr)

    def test_env_contoh_apa_adanya_ditolak(self):
        env = {}
        for baris in (BASE_DIR / '.env.example').read_text(encoding='utf-8').splitlines():
            if baris and not baris.startswith('#') and '=' in baris:
                nama, nilai = baris.split('=', 1)
                env[nama] = nilai
        hasil = muat(**env)
        self.assertNotEqual(hasil.returncode, 0)
        self.assertIn('masih berisi [ISI]. Isi nilainya atau hapus barisnya.', hasil.stderr)

    def test_hsts_bukan_bilangan_bulat_ditolak(self):
        for nilai in ('abc', '3600.5', '1 jam'):
            with self.subTest(nilai=nilai):
                hasil = muat(SECURE_HSTS_SECONDS=nilai)
                self.assertNotEqual(hasil.returncode, 0)
                self.assertIn('ImproperlyConfigured', hasil.stderr)
                self.assertIn(
                    'SECURE_HSTS_SECONDS harus bilangan bulat, contoh 3600.', hasil.stderr
                )

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

    def test_entrypoint_pesan_sandi_db_kosong(self):
        teks = (BASE_DIR / 'scripts' / 'entrypoint.sh').read_text(encoding='utf-8')
        self.assertIn('[-] DB_PASSWORD wajib diisi di .env.', teks)
        self.assertNotIn("os.environ['DB_PASSWORD']", teks)

    def test_env_contoh_hanya_placeholder(self):
        teks = (BASE_DIR / '.env.example').read_text(encoding='utf-8')
        for nama in ('DJANGO_SECRET_KEY', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
                     'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD'):
            self.assertRegex(teks, rf'(?m)^{nama}=\[ISI\]$')

    def test_env_contoh_variabel_opsional_hanya_komentar(self):
        teks = (BASE_DIR / '.env.example').read_text(encoding='utf-8')
        for nama in ('ALLOWED_HOSTS', 'CSRF_TRUSTED_ORIGINS', 'SECURE_HSTS_SECONDS',
                     'CPNS_URL', 'GURU_EMAILS', 'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'):
            with self.subTest(nama=nama):
                self.assertNotRegex(teks, rf'(?m)^{nama}=')
                # Rahasia tanpa contoh nilai; yang lain memberi contoh yang jelas.
                pola = '$' if nama == 'GOOGLE_CLIENT_SECRET' else r'\S'
                self.assertRegex(teks, rf'(?m)^# {nama}={pola}')
        self.assertNotRegex(teks, r'(?m)^# \w+=.*\[ISI\]')

    def test_dockerignore_mengecualikan_env(self):
        baris = (BASE_DIR / '.dockerignore').read_text(encoding='utf-8').splitlines()
        self.assertIn('.env', baris)
        for wajib in ('requirements.txt', 'scripts', 'manage.py', 'config', 'apps',
                      'templates', 'static', '.env.example', '*'):
            self.assertNotIn(wajib, baris)


KODE_UJI_PG = (
    "import json, django\n"
    "from django.conf import settings\n"
    "db = settings.DATABASES['default']\n"
    "print(json.dumps({'engine': db['ENGINE'], 'name': db['NAME'], 'user': db['USER'],"
    " 'host': db['HOST'], 'port': db['PORT'], 'hasher': settings.PASSWORD_HASHERS,"
    " 'hosts': settings.ALLOWED_HOSTS}))\n"
)


class SettingsUjiPostgresTest(SimpleTestCase):
    def muat(self, database_url):
        env = {k: v for k, v in os.environ.items() if k not in VARIABEL}
        env.update({k: '' for k in VARIABEL})
        env['DJANGO_SETTINGS_MODULE'] = 'config.settings.uji_postgres'
        env['DATABASE_URL'] = database_url
        return subprocess.run(
            [sys.executable, '-c', KODE_UJI_PG], cwd=BASE_DIR, env=env,
            capture_output=True, text=True, timeout=120,
        )

    def test_database_url_dipakai(self):
        hasil = self.muat('postgres://postgres:' + SANDI_UJI + '@uji-pg:5432/uji')
        self.assertEqual(hasil.returncode, 0, hasil.stderr)
        data = json.loads(hasil.stdout)
        self.assertEqual(data['engine'], 'django.db.backends.postgresql')
        self.assertEqual(data['name'], 'uji')
        self.assertEqual(data['user'], 'postgres')
        self.assertEqual(data['host'], 'uji-pg')
        self.assertEqual(data['port'], 5432)
        self.assertEqual(data['hasher'], ['django.contrib.auth.hashers.MD5PasswordHasher'])
        self.assertIn('testserver', data['hosts'])

    def test_tanpa_database_url_gagal_jelas(self):
        hasil = self.muat('')
        self.assertNotEqual(hasil.returncode, 0)
        self.assertIn('ImproperlyConfigured', hasil.stderr)
        self.assertIn('DATABASE_URL wajib diisi untuk uji Postgres.', hasil.stderr)
