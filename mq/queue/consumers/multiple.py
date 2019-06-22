from mq.queue.messages import MessageDecoder, Message
from mq.queue.consumers.consumer import BaseQueueConsumer, UnhandledMessageTypeException
from mq.queue.workers.abstract import AbstractWorker
from mq.queue.workers import registry as workers_registry


class MultipleWorkersConsumerMixin(BaseQueueConsumer):
    """
    Consumer that can handle several message types
    Handled_type is a list, appropriate workers are dynamically
    created according to message_type

    You need to define `worker_class` attr explicitly to have possibility
    to call worker's is_ready
    """
    handled_type: (str,) = None

    def decode_message(self, raw_message):
        message = MessageDecoder(raw_message).decoded()
        if message.type not in self.handled_type:
            raise UnhandledMessageTypeException()

        return message

    def new_worker(self, message: Message) -> AbstractWorker:
        worker_class = workers_registry.get(message.type)
        return worker_class(**self.new_worker_kwargs(message))
