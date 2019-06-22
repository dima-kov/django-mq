from mq import messages
from mq.mq_queue.consumers.consumer import QueueConsumer, MultipleWorkersConsumerMixin
from mq.mq_queue.workers import CoordinatesWorker


class NumberMetaConsumer(MultipleWorkersConsumerMixin, QueueConsumer):
    worker_class = CoordinatesWorker
    handled_type = (
        messages.MONETARY_MESSAGE_TYPE, messages.COORDINATES_MESSAGE_TYPE,
        messages.DRRP_COORDINATES_MESSAGE_TYPE, messages.NUMBER_META_COOKIES,
        messages.AGRO_RECEIPT_TYPE, messages.DRRP_EDRPOU_MESSAGE_TYPE,
    )
