from django.conf import settings

from mq.consumers.consumer_number_meta import NumberMetaConsumer
from mq.handlers.base import BaseQueueHandler
from mq.queue.queue_number_meta import NumberMetaQueue


class NumberMetaQueueHandler(BaseQueueHandler):
    queue = NumberMetaQueue()

    consumer_class = NumberMetaConsumer
    consumer_logger = settings.NUMBER_META_CONSUMER_LOGGER_NAME
    consumers_number = settings.NUMBER_META_CONSUMERS_NUMBER
