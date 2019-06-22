from django.conf import settings

from mq.queue.redis import BaseRedisQueue


class PurposeQueue(BaseRedisQueue):
    name = settings.PURPOSE_QUEUE_NAME
