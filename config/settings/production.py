"""
Production settings for agunggumelarsaputra-django.
Uses PostgreSQL, WhiteNoise static compression, and strict security settings.
"""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *

# Semua variabel env yang dibaca base.py dan file ini. Nilai yang masih berisi [ISI]
# berarti baris dari .env.example tersalin tanpa diisi, jadi server tidak boleh jalan.
VARIABEL_ENV = (
    'DJANGO_SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS', 'CSRF_TRUSTED_ORIGINS',
    'DATABASE_URL', 'DB_PASSWORD', 'DB_NAME', 'DB_USER', 'DB_HOST', 'DB_PORT',
    'SECURE_SSL_REDIRECT', 'SESSION_COOKIE_SECURE', 'CSRF_COOKIE_SECURE',
    'SECURE_HSTS_SECONDS', 'STATIC_ROOT', 'MEDIA_ROOT', 'CPNS_URL', 'GURU_EMAILS',
    'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET',
)
for _nama in VARIABEL_ENV:
    if '[ISI]' in os.getenv(_nama, ''):
        raise ImproperlyConfigured(
            f'{_nama} masih berisi [ISI]. Isi nilainya atau hapus barisnya.'
        )

DEBUG = os.getenv('DEBUG', 'False') == 'True'


def env_teks(nama):
    # Nilai kosong dianggap tidak diisi.
    return os.getenv(nama, '').strip()


def env_bool(nama, bawaan):
    nilai = env_teks(nama)
    return bawaan if not nilai else nilai == 'True'


DOMAIN_BAWAAN = [
    'agunggumelarsaputra.com',
    'www.agunggumelarsaputra.com',
    'cpns.agunggumelarsaputra.com',
]

# Secret key wajib dari env. Tidak ada nilai bawaan.
SECRET_KEY = env_teks('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('DJANGO_SECRET_KEY wajib diisi di .env produksi.')
if SECRET_KEY.startswith('django-insecure-') or len(SECRET_KEY) < 50:
    raise ImproperlyConfigured(
        'DJANGO_SECRET_KEY tidak aman. Buat kunci acak baru minimal 50 karakter.'
    )

# Allowed Hosts: daftar eksplisit, wildcard ditolak.
hosts_env = env_teks('ALLOWED_HOSTS')
ALLOWED_HOSTS = (
    [h.strip() for h in hosts_env.split(',') if h.strip()]
    if hosts_env else list(DOMAIN_BAWAAN)
)
if '*' in ALLOWED_HOSTS:
    raise ImproperlyConfigured('ALLOWED_HOSTS tidak boleh berisi "*" di produksi.')

# CSRF Trusted Origins: bawaan hanya https untuk domain sendiri.
csrf_env = env_teks('CSRF_TRUSTED_ORIGINS')
if csrf_env:
    CSRF_TRUSTED_ORIGINS = [c.strip() for c in csrf_env.split(',') if c.strip()]
else:
    CSRF_TRUSTED_ORIGINS = ['https://' + d for d in DOMAIN_BAWAAN]

# Database PostgreSQL. Kata sandi wajib, tanpa nilai bawaan.
DATABASE_URL = env_teks('DATABASE_URL')

if DATABASE_URL:
    import urllib.parse as urlparse
    url = urlparse.urlparse(DATABASE_URL)
    if not url.password:
        raise ImproperlyConfigured('DB_PASSWORD atau DATABASE_URL wajib diisi.')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': url.path[1:],
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port or 5432,
        }
    }
else:
    DB_PASSWORD = env_teks('DB_PASSWORD')
    if not DB_PASSWORD:
        raise ImproperlyConfigured('DB_PASSWORD atau DATABASE_URL wajib diisi.')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env_teks('DB_NAME') or 'ags_db',
            'USER': env_teks('DB_USER') or 'ags_user',
            'PASSWORD': DB_PASSWORD,
            'HOST': env_teks('DB_HOST') or 'db',
            'PORT': env_teks('DB_PORT') or '5432',
        }
    }

# WhiteNoise Compressed Static Files Storage
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Production Security Headers
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# nginx di depan yang mengalihkan http ke https, jadi bawaan False.
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', False)
SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', True)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', True)
try:
    SECURE_HSTS_SECONDS = int(env_teks('SECURE_HSTS_SECONDS') or 3600)
except ValueError:
    raise ImproperlyConfigured(
        'SECURE_HSTS_SECONDS harus bilangan bulat, contoh 3600.'
    ) from None
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'
