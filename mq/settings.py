import os

from django.conf import settings

MQ_REDIS_HOST = getattr(settings, 'MQ_REDIS_HOST', None)

MQ_REDIS_PORT = getattr(settings, 'MQ_REDIS_PORT', None)

MQ_LOGGING_HANDLERS = getattr(settings, 'MQ_HANDLERS', None)

LOGGING = settings.LOGGING

MQ_LOGS_DIRECTORY = '/tmp/mq/'

if MQ_LOGGING_HANDLERS:
    for handler_name in MQ_LOGGING_HANDLERS:
        LOGGING['handlers'][handler_name] = {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(MQ_LOGS_DIRECTORY, '{}.log'.format(handler_name)),
            'formatter': 'worker',
        }
        LOGGING['loggers'][handler_name] = {
            'handlers': [handler_name],
            'level': 'DEBUG',
        }
