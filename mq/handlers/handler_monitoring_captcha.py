from django.conf import settings

from mq.consumers.consumer_monitoring_captcha import MonitoringCaptchaConsumer
from mq.handlers.base import ChainStartQueueHandler
from mq.queue.queue_monitoring import MonitoringNumberQueue
from mq.queue.queue_monitoring_captcha import MonitoringCaptchaQueue


class MonitoringCaptchaQueueHandler(ChainStartQueueHandler):
    queue = MonitoringCaptchaQueue()
    next_queue = MonitoringNumberQueue()

    consumer_class = MonitoringCaptchaConsumer
    consumer_logger = settings.MONITORING_CAPTCHA_CONSUMER_LOGGER_NAME
    consumers_number = settings.MONITORING_CAPTCHA_CONSUMERS_NUMBER
