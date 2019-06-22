from mq import messages
from mq.mq_queue.workers import AbstractWorker, AuthenticatedWorker
from mq.mq_queue.workers.registry import WorkersRegistry
from mq.mq_queue.workers.worker_cookies import CookiesWorker
from mq.mq_queue.workers.worker_coordinates import CoordinatesWorker
from mq.mq_queue.workers.worker_drrp_coordinates import DRRPCoordinatesWorker
from mq.mq_queue.workers.worker_drrp_edrpou import DRRPEdrpouWorker
from mq.mq_queue.workers.worker_monetary import MonetaryValueWorker
from mq.mq_queue.workers.worker_monitoring_authentication import MonitoringAuthenticationWorker
from mq.mq_queue.workers import MonitoringCaptchaWorker
from mq.mq_queue.workers.worker_monitoring_number import MonitoringNumberWorker
from mq.mq_queue.workers import PurposeWorker
from mq.mq_queue.workers import ReceiptWorker

registry = WorkersRegistry()
registry.register(messages.COORDINATES_MESSAGE_TYPE, CoordinatesWorker)
registry.register(messages.MONETARY_MESSAGE_TYPE, MonetaryValueWorker)
registry.register(messages.PURPOSE_MESSAGE_TYPE, PurposeWorker)
registry.register(messages.AGRO_RECEIPT_TYPE, ReceiptWorker)
registry.register(messages.NUMBER_META_COOKIES, CookiesWorker)
registry.register(messages.DRRP_COORDINATES_MESSAGE_TYPE, DRRPCoordinatesWorker)
registry.register(messages.DRRP_EDRPOU_MESSAGE_TYPE, DRRPEdrpouWorker)

registry.register(messages.MONITORING_AUTHENTICATION_MESSAGE_TYPE, MonitoringAuthenticationWorker)
registry.register(messages.MONITORING_CAPTCHA_MESSAGE_TYPE, MonitoringCaptchaWorker)
registry.register(messages.MONITORING_NUMBER_MESSAGE_TYPE, MonitoringNumberWorker)

__all__ = [
    AbstractWorker, AuthenticatedWorker, DRRPCoordinatesWorker, CoordinatesWorker, MonetaryValueWorker,
    MonitoringAuthenticationWorker, MonitoringCaptchaWorker, MonitoringNumberWorker, PurposeWorker,
]
