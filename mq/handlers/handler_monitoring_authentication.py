from django.conf import settings

from mq.consumers.consumer_monitoring_authentication import MonitoringAuthenticationConsumer
from mq.handlers.base import BaseQueueHandler
from mq.queue.queue_authentication import MonitoringAuthenticationQueue


class MonitoringAuthenticationQueueHandler(BaseQueueHandler):
    queue = MonitoringAuthenticationQueue()

    consumer_class = MonitoringAuthenticationConsumer
    consumer_logger = settings.MONITORING_AUTH_CONSUMER_LOGGER_NAME
    consumers_number = settings.MONITORING_AUTH_CONSUMERS_NUMBER
