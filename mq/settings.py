from django.conf import settings

MQ_REDIS_HOST = getattr(settings, 'MQ_REDIS_HOST', None)

MQ_REDIS_PORT = getattr(settings, 'MQ_REDIS_PORT', None)

MQ_LOGGING_HANDLERS = getattr(settings, 'MQ_LOGGING_HANDLERS', None)

MQ_LOGS_DIRECTORY = getattr(settings, 'MQ_LOGS_DIRECTORY', None)

MQ_LOGGING = getattr(settings, 'MQ_LOGGING', {})
