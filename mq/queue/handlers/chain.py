from mq.queue.consumers import ChainEndQueueConsumer, ChainStartQueueConsumer
from mq.queue.handlers.base import BaseQueueHandler
from mq.queue.queue.abstract import AbstractQueue


class ChainStartQueueHandler(BaseQueueHandler):
    """
    Consumes messages from one queue and then push generated messages to next_queue
    """
    next_queue: AbstractQueue = None
    consumer_class = ChainStartQueueConsumer

    def new_consumer_kwargs(self):
        kwargs = super().new_consumer_kwargs()
        kwargs['next_queue'] = self.next_queue
        return kwargs


class ChainEndQueueHandler(BaseQueueHandler):
    """
    Consumes messages from one queue if there are any errors during processing,
    pushes message into previous_queue
    """
    previous_queue: AbstractQueue = None
    consumer_class = ChainEndQueueConsumer

    def new_consumer_kwargs(self):
        kwargs = super().new_consumer_kwargs()
        kwargs['previous_queue'] = self.previous_queue
        return kwargs
