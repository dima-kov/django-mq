from mq import messages
from mq.mq_queue.consumers.consumer import QueueConsumer, MultipleWorkersConsumerMixin
from mq.mq_queue.workers import PurposeWorker


class PurposeConsumer(MultipleWorkersConsumerMixin, QueueConsumer):
    worker_class = PurposeWorker
    handled_type = (messages.PURPOSE_MESSAGE_TYPE,)
