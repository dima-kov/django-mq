from mq import messages
from mq.consumers.consumer import QueueConsumer, MultipleWorkersConsumerMixin
from mq.workers import PurposeWorker


class PurposeConsumer(MultipleWorkersConsumerMixin, QueueConsumer):
    worker_class = PurposeWorker
    handled_type = (messages.PURPOSE_MESSAGE_TYPE,)
