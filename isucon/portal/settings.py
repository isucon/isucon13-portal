"""
Django settings for portal project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import datetime
import os

from isucon.portal import utils as portal_utils

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#_6zme*8g-#1dayt=a$6*&^g3_%gve*ymzw*fdm#96512ldv!z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

IPWARE_META_PRECEDENCE_ORDER = (
    'HTTP_X_FORWARDED_FOR', 'X_FORWARDED_FOR',  # <client>, <proxy1>, <proxy2>
    'HTTP_CLIENT_IP',
    'HTTP_X_REAL_IP',
    'HTTP_X_FORWARDED',
    'HTTP_X_CLUSTER_CLIENT_IP',
    'HTTP_FORWARDED_FOR',
    'HTTP_FORWARDED',
    'HTTP_VIA',
    'REMOTE_ADDR',
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'rest_framework',
    'social_django',
    'widget_tweaks',
    'pgactivity',
    'pglock',
    'isucon.portal',
    'isucon.portal.authentication',
    'isucon.portal.envcheck',
    'isucon.portal.contest',
    # 'isucon.portal.contest.staff',
    # 'isucon.portal.contest.result',
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

AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)


ROOT_URLCONF = 'isucon.portal.urls'

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
                'isucon.portal.contest.context_processors.settings_url',
            ],
        },
    },
]

WSGI_APPLICATION = 'isucon.portal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ATOMIC_REQUESTS': True,
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "authentication.User"


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

LANGUAGE_CODE = 'ja-jp'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

NUMBER_GROUPING = 3

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/opt/app/static/'

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "register"

# アイコンの最大アップロードファイルサイズ(5MB)
MAX_UPLOAD_SIZE = 5242880

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
            'handlers': ['console'],
        },
        'isucon': {
            'level': 'INFO',
            'handlers': ['console'],
        },
    },
}

# AWS
DEFAULT_FILE_STORAGE = "isucon.storage_backends.MediaStorage"
AWS_ACCESS_KEY_ID = "AKIAWFVKEZX5PTZOKL36"
AWS_SECRET_ACCESS_KEY = "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"
AWS_STORAGE_BUCKET_NAME = "isucon13-portal-dev"

SQS_JOB_URLS = {
    "apne1-az1": "https://sqs.ap-northeast-1.amazonaws.com/424484851194/develop-job-queue-apne1-az1.fifo",
    "apne1-az2": "https://sqs.ap-northeast-1.amazonaws.com/424484851194/develop-job-queue-apne1-az2.fifo",
    "apne1-az4": "https://sqs.ap-northeast-1.amazonaws.com/424484851194/develop-job-queue-apne1-az4.fifo",
}

SQS_JOB_RESULT_URL = "https://sqs.ap-northeast-1.amazonaws.com/424484851194/develop-job-result"


# 登録期間
REGISTRATION_START_AT = portal_utils.get_jst_datetime(2023, 8, 1, 10, 0, 0)
REGISTRATION_END_AT = portal_utils.get_jst_datetime(2023, 9, 10, 9, 0, 0)
TEAM_MODIFY_END_AT = portal_utils.get_jst_datetime(2023, 10, 31, 16, 0, 0)

# コンテスト開催期間
# 日付
CONTEST_DATE = datetime.date(2023, 11, 22)

# 時刻
CONTEST_START_TIME = portal_utils.get_jst_time(3, 0, 0)
CONTEST_END_TIME = portal_utils.get_jst_time(20, 0, 0)

# Result
SHOW_RESULT_AFTER = portal_utils.get_jst_datetime(2023, 11, 30, 22, 0, 0)

# Github認証に使うトークン
# TODO: 入れ替える
SOCIAL_AUTH_GITHUB_KEY = '6297ed790692a808fda1'
SOCIAL_AUTH_GITHUB_SECRET = '2a50f16453b05aaa2b024d882ca5030de9858abc'

# Discord
DISCORD_APPLICATION_ID = '1151357797670338641'
DISCORD_SECRET = 'fbd9f57d6ff49ffb1b3ac5cce47e90d8cc95e5fc25f1d601241552305d2e89b5'
DISCORD_OAUTH_CLIENT_ID = '1151357797670338641'
DISCORD_OAUTH_CLIENT_SECRET = 'yPr9Gy0m61o3oAbtI3mKmyy8cgFxz0Ix'

DISCORD_SERVER_ID = "1155732629547659354"
DISCORD_BOT_ACCESS_TOKEN = "MTE1MTM1Nzc5NzY3MDMzODY0MQ.Gzgj4M.1WndtrZJl7QdoMG_wQfSbkV9hU5AoX3pzN8WrE"
DISCORD_USER_ROLE_ID = "1155732748821073930"

BENCHMARK_ABORT_TIMEOUT_SEC = 300

# AWS
ENVCHECK_AMI_ID = "ami-04a7c0e0153437272"
ENVCHECK_AZ_ID = "apne1-az1"
ENVCHECK_DEVELOP = True

CONTEST_AMI_ID = "ami-04a7c0e0153437272"


# チームに所属できる最大人数
MAX_TEAM_MEMBER_NUM = 3
# 最大チーム数
MAX_TEAM_NUM = 1

# チームパスワードとして使う文字群
PASSWORD_LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
# チームパスワードの文字数
PASSWORD_LENGTH = 20

#クーポンとして使う文字列群
COUPON_LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
COUPON_LENGTH = 40

# Redis
REDIS_HOST = '127.0.0.1'
RANKING_TOPN = 30

# Slack
SLACK_ENDPOINT_URL = "https://hooks.slack.com/services/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"

# 外部リンク
MANUAL_URL = '' # TODO:
REGULATION_URL = "https://isucon.net/archives/57768216.html"
DISCORD_URL = '' # TODO:
ISUCON_OFFICIAL_URL = 'http://isucon.net/'
TWITTER_URL = 'https://twitter.com/isucon_official'
TERM_URL = 'https://isucon.net/archives/57774416.html'
BASE_URL = "https://{}".format(os.environ.get("DJANGO_ALLOWED_HOST", "") or "localhost:8000")
