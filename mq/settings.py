from django.conf import settings

MQ_REDIS_HOST = getattr(settings, 'MQ_REDIS_HOST', None)

MQ_REDIS_PORT = getattr(settings, 'MQ_REDIS_PORT', None)

print(settings.INSTALLED_APPS)
