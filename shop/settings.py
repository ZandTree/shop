"""
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import json

with open('/etc/config.json') as fh:
    config = json.load(fh)
SECRET_KEY = config['SECRET_KEY']
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR,'templates')

DEBUG = False

ALLOWED_HOSTS = ['188.166.71.144','houseofmydream.nl','localhost']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    #third party
    'bootstrap4',
    'django_cleanup',
    'mptt',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'paypal.standard.ipn',
    'stripe',
    #custom apps
    'prods',
    'search',
    'tags',
    'profiles',
    'orders',
    'payments',
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

ROOT_URLCONF = 'shop.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER':DB_USER,
        'PASSWORD':DB_PSW,
        'HOST':'localhost',
        'PORT':'5432',

    }
}


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # my own function = in dir shop dir context_processors func list_categories
                'prods.context_processors.count_items_cart',
                'prods.context_processors.list_categories',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
SITE_ID = 1

WSGI_APPLICATION = 'shop.wsgi.application'



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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = None #"optional"
ACCOUNT_USERNAME_REQUIRED = False
LOGIN_URL= '/account/login'
LOGIN_URL_REDIRECT = "/"
ACCOUNT_EMAIL_SUBJECT_PREFIX = "Subject: "
# auto loggin in after confirmation(otherwise will be redirected to log-in)
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

ACCOUNT_ADAPTER = 'adapter.AccountAdapter'

#paypal settings

PAYPAL_RECEIVER_EMAIL = config.get("PAYPAL_RECEIVER_EMAIL")
PAYPAL_TEST = True

# stripe settings
STRIPE_PUBLISHABLE_KEY = config.get("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = config.get('STRIPE_TEST_SECRET_KEY')
IDEAL_API = config.get('IDEALWORD')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = config.get("MY_EMAIL")
EMAIL_HOST_PASSWORD = config.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True




STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media/')

INTERNAL_IPS = ['127.0.0.1']

# try:
#     from .local_settings import *
# except ImportError:
#     from .prod_settings import *
