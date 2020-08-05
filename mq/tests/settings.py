import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '!q*gy^010u-wewhx9fhf3r!_-scvw&5=+l!f9es_rn#_q2llq1'

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.auth',
    'mq',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mq',
        'USER': 'mq',
        'PASSWORD': 'mq',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'apps/dashboard/comparision/templates'),
        ],
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

# redis
MQ_REDIS_HOST = 'localhost'

MQ_REDIS_PORT = 6379

# loggers

LOGGING = {}

COORDINATES_LOGGER = 'coordinates'

MQ_LOGGING_LOGGERS = [COORDINATES_LOGGER]

MQ_LOGGING_DIRECTORY = '/Users/dima/projects/moze/logs'

from mq.logging import configure_logging  # noqa

configure_logging(LOGGING, MQ_LOGGING_LOGGERS, MQ_LOGGING_DIRECTORY)

MQ_FLUSH_ERRORS_DAYS = 10
