from mq import messages
from mq.consumers.consumer import ChainStartQueueConsumer


class MonitoringCaptchaConsumer(ChainStartQueueConsumer):
    handled_type = messages.MONITORING_CAPTCHA_MESSAGE_TYPE
