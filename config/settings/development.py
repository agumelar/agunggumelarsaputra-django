"""
Development settings for agunggumelarsaputra-django.
Uses SQLite and DEBUG=True for local testing.
"""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# SQLite Database for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Development email backend (Console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
