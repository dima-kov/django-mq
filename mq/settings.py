import os

try:
    import django  # noqa

    DJANGO_INSTALLED = True
except ImportError:
    DJANGO_INSTALLED = False


def settings_factory(name, default=None):
    if DJANGO_INSTALLED is True:
        return settings_django(name, default)
    else:
        return settings_env(name, default)


def settings_django(name, default=None):
    from django.conf import settings

    return getattr(settings, name, default)


def settings_env(name, default=None):
    return os.environ.get(name, default)


MQ_REDIS_HOST = settings_factory('MQ_REDIS_HOST', 'localhost')

MQ_REDIS_PORT = settings_factory('MQ_REDIS_PORT', '6379')

MQ_LOGGING_HANDLERS = settings_factory('MQ_LOGGING_HANDLERS')

MQ_LOGS_DIRECTORY = settings_factory('MQ_LOGS_DIRECTORY')

MQ_LOGGING = settings_factory('MQ_LOGGING', {})

# Period in days after which resolved errors will be deleted
MQ_FLUSH_ERRORS_DAYS = settings_factory('MQ_FLUSH_ERRORS_DAYS')
