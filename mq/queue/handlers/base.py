import asyncio

import uvloop

from mq.queue.consumers import QueueConsumer
from mq.queue.queue.abstract import AbstractQueue


class BaseQueueHandler(object):
    queue: AbstractQueue = None
    consumer_class = QueueConsumer

    consumers_number = 10  # default value
    consumer_logger = '{consumer_item}'

    def __init__(self):
        super(BaseQueueHandler, self).__init__()
        self.queue.processing_to_wait()

    def handle(self):
        consumers = self.generate_consumers()
        print('Consumers registered')

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()
        try:
            print('Start handling')
            consumers = [i.consume() for i in consumers]
            loop.run_until_complete(asyncio.wait(consumers))
        except KeyboardInterrupt:
            pass
        finally:
            print('Shutdown ...')
            [t.cancel() for t in asyncio.Task.all_tasks()]
            print('Pending tasks canceled')

            self.unregister_consumers(consumers)
            print('Consumers unregistered')

            print('Ensure future - sleep 2s')
            loop.run_until_complete(asyncio.ensure_future(asyncio.sleep(2)))

            loop.stop()
            print('Loop stopped')

        loop.close()
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
