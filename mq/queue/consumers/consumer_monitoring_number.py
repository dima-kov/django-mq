from mq import messages
from mq.mq_queue.consumers.consumer import ChainEndQueueConsumer, AuthenticatedQueueConsumer, \
    MultipleWorkersConsumerMixin
from mq.mq_queue.workers import MonitoringNumberWorker


class MonitoringNumberConsumer(MultipleWorkersConsumerMixin, ChainEndQueueConsumer, AuthenticatedQueueConsumer):
    worker_class = MonitoringNumberWorker
    handled_type = (messages.MONITORING_NUMBER_MESSAGE_TYPE,)
