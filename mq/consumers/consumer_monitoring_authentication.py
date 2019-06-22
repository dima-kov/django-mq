from mq import messages
from mq.consumers.consumer import QueueConsumer


class MonitoringAuthenticationConsumer(QueueConsumer):
    handled_type = messages.MONITORING_AUTHENTICATION_MESSAGE_TYPE
