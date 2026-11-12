"""
Development settings for agunggumelarsaputra-django.
Uses SQLite and DEBUG=True for local testing.
"""

import os

from .base import *

DEBUG = True

# Kunci lokal, hanya untuk development.
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY') or 'django-insecure-agshighcraft-fallback-key-2026'

# Subdomain cpns di mesin lokal (port dev server 8010).
CPNS_URL = "http://cpns.localhost:8010/"

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', 'testserver', '.localhost', 'cpns.localhost', 'cpns.agunggumelarsaputra.com']

# SQLite Database for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Development email backend (Console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
