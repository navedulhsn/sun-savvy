"""
Django settings for sunsavvy project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to use python-decouple for environment variables, fallback to os.environ
try:
    from decouple import config
    USE_DECOUPLE = True
except ImportError:
    USE_DECOUPLE = False
    def config(key, default=''):
        return os.environ.get(key, default)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-sunsavvy-dev-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'solar.apps.SolarConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sunsavvy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'sunsavvy.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# API Keys (set these in environment variables or .env file)
OPENWEATHER_API_KEY = config('OPENWEATHER_API_KEY', default='')
SOLCAST_API_KEY = config('SOLCAST_API_KEY', default='')
GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY', default='')
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')

# Email Configuration
# For Gmail SMTP, you need to:
# 1. Enable 2-Step Verification on your Google account
# 2. Generate an App Password: https://myaccount.google.com/apppasswords
# 3. Use that app password (not your regular password) in EMAIL_HOST_PASSWORD
# 4. Set environment variables or create a .env file with:
#    EMAIL_HOST_USER=your-email@gmail.com
#    EMAIL_HOST_PASSWORD=your-16-character-app-password

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')  # Your Gmail address
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')  # Your Gmail App Password
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='SunSavvy <noreply@sunsavvy.com>')

# Fallback to console if email credentials not set (for development)
if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    if DEBUG:
        print("WARNING: Email not configured. Emails will be printed to console.")
        print("   To enable email sending:")
        print("   1. Create a .env file in project root")
        print("   2. Add: EMAIL_HOST_USER=your-email@gmail.com")
        print("   3. Add: EMAIL_HOST_PASSWORD=your-app-password")
        print("   4. See EMAIL_SETUP.md for detailed instructions")

