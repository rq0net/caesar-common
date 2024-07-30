"""
Django settings for project 'caesar_auth.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/

List of settings that the project as to have to be ready for production:

- General settings:
    - SECRET_KEY: the Django secret key
    - ENABLE_DEBUG: False by default, set to 1 to enable it.
    - ALLOWED_HOSTS: empty by default, use comma-separated list.
    - LOGGING_CONFIG: default None.
    - TIME_ZONE: default 'UTC', list: http://pytz.sourceforge.net/#what-is-utc
    - PATH_TO_STORE_FILE: default BASE_DIR + '/files/'
- DB-related settings:
    - DB_HOST: default 'localhost'
    - DB_USER: default 'user'
    - DB_NAME: default 'project_db'
    - DB_PASS: default 'passwd' in debug mode ssm 'db_password' in production.
    - DB_PORT: default '5432'
- Email settings:
    - rq0net@gmail.com
- Sentry settings:
    - SENTRY_DSN: default is None, set to a valid DSN to enable sentry.
    - SENTRY_RELEASE: default 'local', set to 'stage', 'live', etc.
- AWS settings:
    - TODO
- Silk profiler:
    - ENABLE_SILK: False by default, set to 1 to enable it.

"""

import os
import sys
from distutils.util import strtobool

gettext = lambda s: s
DATA_DIR = os.path.dirname(os.path.dirname(__file__))

APP_NAME = "COMMON"

# import boto3 as boto3
#
# # for the secrets
# aws_client = boto3.client('ssm', region_name='eu-west-1')
# response = aws_client.get_parameters(
#     Names=[
#         'db_password',
#         'email_password',
#         'django_secret_key',
#         'stats_api_key',
#     ],
#     WithDecryption=True
# )
# secrets = {p.get('Name'): p.get('Value') for p in response.get('Parameters')}
secrets = {}

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATH_TO_STORE_FILE = os.environ.get(
    'PATH_TO_STORE_FILE', default=BASE_DIR + '/files/')
os.makedirs(PATH_TO_STORE_FILE, exist_ok=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
# or with a file
# with open('/etc/secret_key.txt') as f:
#     SECRET_KEY = f.read().strip()

# Are in test mode?
TESTING = 'test' or '-k e2e' in sys.argv

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = strtobool(os.getenv('ENABLE_DEBUG', 'false'))

# Allowed hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
if DEBUG:
    ALLOWED_HOSTS.extend(['127.0.0.1', 'localhost', '0.0.0.0'])

INTERNAL_IPS = [
    '127.0.0.1',
]


# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

ADMINS = (
    ('Author', 'rq0net@gmail.com'),
)

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': int(os.getenv('DJANGO_PAGINATION_LIMIT', 20)),
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
    
    'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.BasicAuthentication',  # require for /docs
        'rest_framework.authentication.TokenAuthentication',
    ],
    
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'rest_framework.permissions.IsAuthenticated',
    # ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}



# Application definition
INSTALLED_APPS = [
    # Core authentication framework and its default models.
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Manages sessions across requests
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # Associates users with requests using sessions.
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "common.rest.middleware.changeLog.ChangeLogMiddleware",
]

ROOT_URLCONF = '%s.urls' % APP_NAME.lower()

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = '%s.wsgi.application' % APP_NAME.lower()



DB_ENGINE = 'django.db.backends.postgresql'
DB_HOST = os.getenv('POSTGRESQL_DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('POSTGRESQL_DB_PORT', '5432')
DB_USER = os.getenv('POSTGRESQL_DB_USER', 'user')
DB_PASS = os.getenv('POSTGRESQL_DB_PASS', 'passwd')
DB_NAME = os.getenv('%s_DB_NAME' % APP_NAME, 'caesar_%s' % APP_NAME.lower())

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {   # todo; here for the fanatic pep8 line len max 79, tell me how to solve it???
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
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', default='zh-hans')

LANGUAGES = (
    ## Customize this
    ('en', gettext('English')),
    ('zh-hans', gettext('Chinese')),
)

# list: http://pytz.sourceforge.net/#what-is-utc
TIME_ZONE = os.environ.get('TIME_ZONE', default='Asia/Singapore')
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_ROOT = os.environ.get('STATIC_ROOT', default=os.path.join(DATA_DIR, 'static'))

STATIC_URL = '/static/'

# Some media files if you need it else remove it
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')
MEDIA_URL = '/media/'

# # Sentry
# SENTRY_DSN = os.getenv('SENTRY_DSN', None)
# if SENTRY_DSN is not None:
#     import raven
#     SENTRY_RELEASE = os.getenv('SENTRY_RELEASE', 'local')
#
#     INSTALLED_APPS.append('raven.contrib.django.raven_compat')
#     RAVEN_CONFIG = {
#         'dsn': SENTRY_DSN,
#         'release': SENTRY_RELEASE,
#     }

# Once you’ve set up HTTPS, enable the following settings.
# Set this to True to avoid transmitting the CSRF cookie over HTTP accidentally.
# usefull for BasicAuthentication and SessionAuthentication
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(asctime)s] %(message)s',
        },
        'verbose': {
            'format':
                # todo; here for the fanatic pep8 line len max 79, tell me how to solve it???
                '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'slack_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django_slack.log.SlackExceptionHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['slack_admins', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO'
        },
    }
}



AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]



if DEBUG:
    INSTALLED_APPS += ['debug_toolbar',]
    MIDDLEWARE += [ 
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]


# KeyCloak
USE_KEYCLOAK = strtobool(os.getenv('USE_KEYCLOAK', 'false'))

if USE_KEYCLOAK is not None:
    INSTALLED_APPS += [
        'django_keycloak.apps.KeycloakAppConfig',
        'caesar_user',
    ]

    MIDDLEWARE += [ 
        'django_keycloak.middleware.BaseKeycloakMiddleware', 
        'django_keycloak.middleware.KeycloakStatelessBearerAuthenticationMiddleware',
    ]
    PASSWORD_HASHERS = [
        'django_keycloak.hashers.PBKDF2SHA512PasswordHasher',
    ]
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend', 
        'django_keycloak.auth.backends.KeycloakAuthorizationCodeBackend',
        'django_keycloak.auth.backends.KeycloakIDTokenAuthorizationBackend',
    ]
    
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] += ['django_keycloak.auth.authentication.KeycloakIDAuthentication', ]
    
    
    KEYCLOAK_OIDC_PROFILE_MODEL = 'django_keycloak.OpenIdConnectProfile'
    KEYCLOAK_BEARER_AUTHENTICATION_EXEMPT_PATHS = [
        r'^admin/',
        r'^docs/',
    ]
#     KEYCLOAK_SKIP_SSL_VERIFY = True
    
    LOGIN_URL = 'keycloak_login'

INSTALLED_APPS += ["django_slack",]
SLACK_TOKEN=os.environ.get("SLACK_TOKEN", None)
SLACK_CHANNEL=os.environ.get("SLACK_CHANNEL", '#test')

PUSHER_SERVER = os.getenv('PUSHER_SERVER', "https://api.cwcdn.com/api/v1/pusher/")
CMDB_SERVER = os.getenv('CMDB_SERVER', "https://api.cwcdn.com/api/v1/cmdb/")
PLAN_SERVER = os.getenv('PLAN_SERVER', "https://api.cwcdn.com/api/v1/plan/")


ALIYUN = {
    "ACCESS_KEY":  os.getenv('ALIYUN_ACCESS_KEY', ''),
    "ACCESS_SECRET":  os.getenv('ALIYUN_ACCESS_SECRET', ''),
    "LOG_ENDPOINT": os.getenv('ALIYUN_LOG_ENDPOINT', ''),
    "LOG_PROJECT": os.getenv('ALIYUN_LOG_PROJECT', 'cdnnodes'),
    "LOG_LOGSTORE": os.getenv('ALIYUN_LOG_LOGSTORE', 'nginx'),
}



# Config for celery to recode the deploy result
INSTALLED_APPS += [
    'common.rest',
]
# Config for celery to recode the deploy result
INSTALLED_APPS += [
    'django_celery_results',
]


TELEGRAMBOT = {
    "TOKEN": os.getenv('TELEGRAMBOT_TOKEN', ''),
    "DEFAULT_CHAT_ID": os.getenv('TELEGRAMBOT_DEFAULT_CHAT_ID', ''),
}

# Config for celery to recode the deploy result
INSTALLED_APPS += [
    'zone',
]

ELASTICSEARCH_API_HOST=os.getenv('ELASTICSEARCH_API_HOST','')
ELASTICSEARCH_API_KEY=os.getenv('ELASTICSEARCH_API_KEY','')