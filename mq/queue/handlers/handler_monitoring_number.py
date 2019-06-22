from django.conf import settings

from mq.mq_queue.consumers.consumer_monitoring_number import MonitoringNumberConsumer
from mq.mq_queue.handlers import AuthenticatedQueueHandler, ChainEndQueueHandler
from mq.mq_queue.queue.queue_monitoring import MonitoringNumberQueue
from mq.mq_queue.queue.queue_monitoring_captcha import MonitoringCaptchaQueue


class MonitoringQueueHandler(AuthenticatedQueueHandler, ChainEndQueueHandler):
    queue = MonitoringNumberQueue()
    previous_queue = MonitoringCaptchaQueue()

    consumer_class = MonitoringNumberConsumer
    consumer_logger = settings.MONITORING_NUMBER_CONSUMER_LOGGER_NAME
    consumers_number = settings.MONITORING_NUMBER_CONSUMERS_NUMBER
