from mq import messages
from mq.consumers.consumer import ChainEndQueueConsumer, AuthenticatedQueueConsumer, \
    MultipleWorkersConsumerMixin
from mq.workers import MonitoringNumberWorker


class MonitoringNumberConsumer(MultipleWorkersConsumerMixin, ChainEndQueueConsumer, AuthenticatedQueueConsumer):
    worker_class = MonitoringNumberWorker
    handled_type = (messages.MONITORING_NUMBER_MESSAGE_TYPE,)
