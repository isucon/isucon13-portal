import os
from isucon.portal.settings import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+2j!(q)l=h9u6x+&i2vv3==lc2@5&3njd=ak1y84j#49^=05+g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.environ.get('DJANGO_DEBUG', "true").lower() == "true" else False

ALLOWED_HOSTS = [os.environ.get('DJANGO_ALLOWED_HOST', "*"), "localhost"]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES_SQLITE3 = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ATOMIC_REQUESTS': True,
    }
}

DATABASES_POSTGRES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DATABASE_NAME', "isucon"),
        'USER': os.environ.get('DATABASE_USER', "isucon"),
        'PASSWORD': os.environ.get('DATABASE_PASS', "password"),
        'HOST': os.environ.get('DATABASE_HOST', "postgres"),
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
    }
}

DATABASE_TYPE = os.environ.get('DJANGO_DATABASE_TYPE', "sqlite3").lower()

DATABASES = {}
if DATABASE_TYPE == "sqlite3":
    DATABASES = DATABASES_SQLITE3
elif DATABASE_TYPE == "postgres":
    DATABASES = DATABASES_POSTGRES
else:
    raise ValueError("Invalid DJANGO_DATABASE_TYPE '{}'".format(DATABASE_TYPE))

REDIS_HOST = os.environ.get('REDIS_HOST', "redis")
REDIS_RANKING_TOPN = os.getenv('REDIS_RANKING_TOPN', 30)

SOCIAL_AUTH_GITHUB_KEY = os.environ.get("GITHUB_KEY", "")
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get("GITHUB_SECRET", "")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = "/opt/app/static/"


# AWS
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "isucon13-portal-dev")

# 動作設定

# 登録期間
REGISTRATION_START_AT = portal_utils.get_jst_datetime(2023, 8, 22, 10, 0, 0)
REGISTRATION_END_AT = portal_utils.get_jst_datetime(2023, 9, 10, 9, 0, 0)

# 最大チーム数
MAX_TEAM_NUM = 2


# アプリケーション固有設定

BENCHMARK_MAX_CONCURRENCY = 3
BENCHMARK_ABORT_TIMEOUT_SEC = 300

SLACK_ENDPOINT_URL = os.environ.get('SLACK_ENDPOINT_URL', "https://slack.com/api/chat.postMessage")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {},
    'handlers': {
        'slack_admins': {
            'level': 'ERROR',
            'filters': [],
            'class': 'isucon.portal.logging.SlackExceptionHandler',
        },
        'console': {
            'level': 'INFO',
            'filters': [],
            'class': 'logging.StreamHandler',
        },
    },
    'formatters': {
        'simple': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s a',
        }
    },
    'loggers': {
        'django': {
            'level': 'INFO',
            'handlers': ['slack_admins', 'console'],
        },
        'isucon': {
            'level': 'INFO',
            'handlers': ['slack_admins', 'console'],
        },
    },
}
