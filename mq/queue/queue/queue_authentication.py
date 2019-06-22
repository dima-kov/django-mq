from django.conf import settings

from mq.mq_queue.queue.redis import BaseRedisQueue


class MonitoringAuthenticationQueue(BaseRedisQueue):
    name = settings.MONITORING_AUTHENTICATION_QUEUE_NAME
