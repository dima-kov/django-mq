from django.conf import settings


MQ_REDIS_HOST = getattr(settings, 'MQ_REDIS_HOST', None)
print(MQ_REDIS_HOST, getattr(settings, 'MQ_REDIS_HOST', None), settings.TEMPLATES)

MQ_REDIS_PORT = getattr(settings, 'MQ_REDIS_PORT', None)
