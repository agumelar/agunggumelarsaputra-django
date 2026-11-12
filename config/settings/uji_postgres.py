"""Settings untuk menjalankan suite tes di Postgres sementara (lihat docs/cpns/rilis.md D.1).

Dasarnya development (ALLOWED_HOSTS dev, storage bawaan). Hanya database yang diganti.
"""

import os
import urllib.parse as urlparse

from django.core.exceptions import ImproperlyConfigured

from .development import *

DATABASE_URL = os.getenv('DATABASE_URL', '').strip()
if not DATABASE_URL:
    raise ImproperlyConfigured(
        'DATABASE_URL wajib diisi untuk uji Postgres. '
        'Contoh: postgres://postgres:<sandi>@uji-pg:5432/uji'
    )

_url = urlparse.urlparse(DATABASE_URL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': _url.path[1:],
        'USER': _url.username,
        'PASSWORD': _url.password,
        'HOST': _url.hostname,
        'PORT': _url.port or 5432,
    }
}

# Hasher cepat, hanya untuk tes.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
