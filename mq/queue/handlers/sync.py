from mq.queue.consumers.sync import SyncQueueConsumer
from mq.queue.exceptions import TerminatedException
from mq.queue.queue.abstract import AbstractQueue


class SyncQueueHandler(object):
    queue: AbstractQueue = None
    consumer_class = SyncQueueConsumer
    consumer_logger = '{consumer_item}'

    def __init__(self):
        self.queue.processing_to_wait()

    def handle(self):
        cids = self.queue.consumers_register(1)
        consumer = self.new_consumer(cids[0])

        try:
            print('Start handling')
            consumer.consume()
        except (KeyboardInterrupt, TerminatedException):
            pass
        finally:
            print('Shutdown ...')
            consumer.unregister()
            print('Consumer unregistered')

    def new_consumer(self, cid):
        return self.consumer_class(cid=cid, **self.new_consumer_kwargs())

    def new_consumer_kwargs(self):
        return {
            'queue': self.queue,
            'logger_name': self.consumer_logger,
        }
