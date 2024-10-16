"""
Django settings for dnachron_mutations project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os

from tools.constant import ReferencesBuilds

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "h*b@r@a004-#^+7fma@r49_frbhqsaq8&^gro=!sy=q1!o@ht6"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "models",
]

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
if os.path.exists(BASE_DIR / "dnachronYdb/dnachronYdb.sqlite3"):
    database_file = BASE_DIR / "dnachronYdb/dnachronYdb.sqlite3"
    DATABASE_BUILD = ReferencesBuilds.HG38
    DATABASE_YBROWSE_COLUMN = False
else:
    database_file = BASE_DIR / "ymutations/ymutations.sqlite3"
    DATABASE_BUILD = ReferencesBuilds.CP086569_2
    DATABASE_YBROWSE_COLUMN = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": database_file,
    },
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = False

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
