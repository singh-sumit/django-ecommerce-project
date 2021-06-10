from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(5%pnw516&xrytfz&sk(1pcwsw2)6)v28#!pfmnp4x_#3ok-uq'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'DATABASE_NAME',
        'USER': 'DATABASE_USER',
        'PASSWORD': 'DATABASE_PWD',
        'HOST': 'localhost',
        'PORT': 3306,
    }
}

# configure e-mail setup for password reset
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailtrap.io'
EMAIL_PORT = '2525'
EMAIL_HOST_USER = 'USER_HOST_NAME'
EMAIL_HOST_PASSWORD = 'USER_PWD'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
