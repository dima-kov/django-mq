from django.conf import settings

from mq.mq_queue.queue.redis import BaseRedisQueue


class MonitoringCaptchaQueue(BaseRedisQueue):
    name = settings.MONITORING_CAPTCHA_QUEUE_NAME
