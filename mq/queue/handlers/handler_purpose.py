from django.conf import settings

from mq.mq_queue.consumers.consumer_purpose import PurposeConsumer
from mq.mq_queue.handlers import BaseQueueHandler
from mq.mq_queue.queue.queue_purpose import PurposeQueue


class PurposeQueueHandler(BaseQueueHandler):
    queue = PurposeQueue()

    consumer_class = PurposeConsumer
    consumer_logger = settings.PURPOSE_CONSUMER_LOGGER_NAME
    consumers_number = settings.PURPOSE_CONSUMERS_NUMBER
