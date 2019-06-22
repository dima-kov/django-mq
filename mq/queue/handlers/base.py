import asyncio

from apps.core.helpers import AsyncLoop
from mq.mq_queue.common import TerminatedException
from mq.mq_queue.consumers.consumer import QueueConsumer, ChainStartQueueConsumer, \
    AuthenticatedQueueConsumer, ChainEndQueueConsumer
from mq.mq_queue.queue.abstract import AbstractQueue
from mq.mq_queue.queue.queue_authentication import MonitoringAuthenticationQueue


class BaseQueueHandler(AsyncLoop):
    queue: AbstractQueue = None
    consumer_class = QueueConsumer

    consumers_number = 10  # default value
    consumer_logger = '{consumer_item}'

    def __init__(self, *args, **kwargs):
        super(BaseQueueHandler, self).__init__(*args, **kwargs)
        self.queue.processing_to_wait()

    def handle(self):
        consumers = self.generate_consumers()
        print('Consumers registered')
        try:
            print('Start handling')
            self.run_multiple([i.consume() for i in consumers])
        except (KeyboardInterrupt, TerminatedException):
            pass
        finally:
            print('Shutdown ...')
            [t.cancel() for t in asyncio.Task.all_tasks()]
            print('Pending tasks canceled')

            self.unregister_consumers(consumers)
            print('Consumers unregistered')

            self.loop.stop()
            print('Loop stopped')

        self.loop.close()
        print('Loop closed')

    def generate_consumers(self):
        cids = self.queue.consumers_register(self.consumers_number)
        return [self.new_consumer(cid) for cid in cids]

    def new_consumer(self, cid):
        return self.consumer_class(cid=cid, **self.new_consumer_kwargs())

    def new_consumer_kwargs(self):
        return {
            'queue': self.queue,
            'logger_name': self.consumer_logger,
        }

    @staticmethod
    def unregister_consumers(consumers):
        return [c.unregister() for c in consumers]


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


class AuthenticatedQueueHandler(BaseQueueHandler):
    """
    Connects Authentication queue during init
    """
    auth_queue = MonitoringAuthenticationQueue()
    consumer_class: type(AuthenticatedQueueConsumer) = AuthenticatedQueueConsumer

    def new_consumer_kwargs(self):
        kwargs = super().new_consumer_kwargs()
        kwargs['auth_queue'] = self.auth_queue
        return kwargs
