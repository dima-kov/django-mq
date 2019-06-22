from django.core.checks import Warning, Error, register, Tags
from mq import settings


W001 = Error('Invalid MQ_REDIS_HOST parameter',
             hint='Set a non empty string to settings.MQ_REDIS_HOST',
             id='mq.W001')
W002 = Warning('Invalid MQ_REDIS_PORT parameter',
               hint='Set a non empty string to settings.MQ_REDIS_PORT',
               id='mq.W002')


@register(Tags.compatibility)
def check_settings(app_configs, **kwargs):
    errors = []
    if not settings.MQ_REDIS_HOST:
        errors.append(W001)

    if not settings.MQ_REDIS_PORT:
        errors.append(W002)

    return errors
