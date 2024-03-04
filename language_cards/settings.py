"""
Django settings for language_cards project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-xiwq@wx7n*g5)kpk$gwpceg^9i&k)uf)oz7iq4c6&oylaj9j)8')

# For example, for a site URL at 'web-production-3640.up.railway.app'
# (replace the string below with your own site URL):
ALLOWED_HOSTS = ['languagecards-production.up.railway.app', '127.0.0.1', 'localhost']

CSRF_TRUSTED_ORIGINS = ['https://languagecards-production.up.railway.app']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'language_cards.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'language_cards.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Update database configuration from $DATABASE_URL environment variable (if defined)

if os.environ.get('ENV', False):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get('PGDATABASE', False),
            "USER": os.environ.get('PGUSER', False),
            "PASSWORD": os.environ.get('PGPASSWORD', False),
            "HOST": os.environ.get('PGHOST', False),
            "PORT": os.environ.get('PGPORT', False),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


if os.environ.get('ENV', False):
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=500,
        conn_health_checks=True,
    )







# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# The absolute path to the directory where collectstatic will collect static files for deployment.
env = os.environ.get('ENV', False)

if env:
    STATIC_ROOT = BASE_DIR / 'staticfiles'
else:
    DEBUG = True
    MEDIA_ROOT = BASE_DIR / 'media/'
    MEDIA_URL = 'media/'

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'core.auth_backends.EmailAuthBackend',
]


# settings to store media files in GCS
from google.oauth2 import service_account

# if it is True then all media files will be stored in GSC, in other case - locally on /media
SAVE_MEDIA_ON_GSC = True

if SAVE_MEDIA_ON_GSC:
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
       str(BASE_DIR / 'credentials.json')
    )

    GS_BUCKET_NAME = 'upload_photos_bucket'

    STORAGES = {
       "default": {
           "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
           "OPTIONS": {},
       },
       "staticfiles": {
           "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
       },
    }
