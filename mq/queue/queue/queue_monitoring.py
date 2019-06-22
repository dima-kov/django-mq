from django.conf import settings

from mq.mq_queue.queue.redis import BaseRedisQueue


class MonitoringNumberQueue(BaseRedisQueue):
    name = settings.MONITORING_NUMBER_QUEUE_NAME
    capacity = 6
