"""
Django settings for GHOST Personal AI Intelligence System.
Loads operational parameters from the existing .env file using pydantic-settings (via config.py).
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Import GHOST settings from existing config module (pydantic-settings loads .env automatically)
from config import settings as ghost_settings

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ghost_settings.gateway_secret or 'ghost-django-insecure-default-key-change-me'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'daphne',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'corsheaders',
    'channels',
    'ghost_app',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

# CORS settings (replaces FastAPI CORSMiddleware with allow_origins=["*"])
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['*']
CORS_ALLOW_HEADERS = ['*']

ROOT_URLCONF = 'ghost_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'ghost_app' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'ghost_project.wsgi.application'
ASGI_APPLICATION = 'ghost_project.asgi.application'

# Database — SQLite at database/ghost.db (managed by raw SQLite layer, not Django ORM)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'database' / 'ghost.db',
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django Channels — in-memory channel layer for development
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# GHOST operational settings (re-exported for convenience)
GHOST_CALLSIGN = ghost_settings.callsign
GHOST_OPERATOR_NAME = ghost_settings.operator_name
GHOST_SECURITY_LEVEL = ghost_settings.security_level
GHOST_HOST = ghost_settings.host
GHOST_PORT = ghost_settings.port
GHOST_VOICE_NAME = ghost_settings.voice_name
