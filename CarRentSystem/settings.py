"""
Django settings for CarRentSystem project.

Generated by 'django-admin_pages startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.


BASE_DIR = Path(__file__).resolve().parent.parent

import environ

root = environ.Path(__file__)
env = environ.Env()
environ.Env.read_env()  # reading .env file

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

DEBUG = env.bool('DEBUG')
SECRET_KEY = env.str('SECRET_KEY')
UKLON_USER = env.str('UKLON_USER')
UKLON_PASS = env.str('UKLON_PASS')

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'constance',
    'constance.backends.database',
    'ajax_select',
    'balance',
    'carmanagment',
    'main_menu',
    'vue_utils'
]

# see https://github.com/jazzband/django-constance
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'


def list_account():
    from balance.models import Account
    return Account.objects.all()


def list_investors():
    from carmanagment.models import Investor
    return Investor.objects.all()


def list_cash():
    from balance.models import CashBox
    return CashBox.objects.all()


CONSTANCE_ADDITIONAL_FIELDS = {
    'all_select': ['carmanagment.admin_pages.MyModelChoiceField', {
        'widget': 'django.forms.Select',
        'queryset': list_account
    }],
    'investor_select': ['carmanagment.admin_pages.MyModelChoiceField', {
        'widget': 'django.forms.Select',
        'queryset': list_investors
    }],
    'cashbox_select': ['carmanagment.admin_pages.MyModelChoiceField', {
        'widget': 'django.forms.Select',
        'queryset': list_cash
    }],
}

CONSTANCE_CONFIG = {
    'USD_CURRENCY': (27., 'Курс доллара США', float),
    'FUEL_A95': (30., 'Стоимость литра А95', float),
    'FUEL_A92': (29., 'Стоимость литра А95', float),
    'FUEL_DISEL': (28., 'Стоимость литра Дизеля', float),
    'FUEL_GAS': (12., 'Стоимость литра Газа', float),
    'FUEL_A98': (32., 'Стоимость литра А98', float),
    'FUEL_A95+': (30., 'Стоимость литра А95+', float),
    'FUEL_DISEL+': (28., 'Стоимость литра Дизеля+', float),
    'FIRM': (None, 'Акаунт фирмы', 'investor_select'),
    'CASH': (None, 'Касса по умолчанию', 'cashbox_select'),
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'audit_log.middleware.JWTAuthMiddleware',
    'audit_log.middleware.UserLoggingMiddleware',
]

ROOT_URLCONF = 'CarRentSystem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'CarRentSystem.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
