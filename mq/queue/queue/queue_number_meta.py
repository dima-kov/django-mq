from django.conf import settings

from mq.mq_queue.queue.redis import BaseRedisQueue


class NumberMetaQueue(BaseRedisQueue):
    name = settings.NUMBER_META_QUEUE_NAME
