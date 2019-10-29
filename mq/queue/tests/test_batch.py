from unittest import TestCase

from memory_profiler import profile

from mq.queue.handlers.base import BaseQueueHandler
from mq.queue.messages import MessageType
from mq.queue.queue.redis import RedisQueue
from mq.queue.workers import registry, AbstractWorker


class TestQueue(RedisQueue):
    name = "test"

    type_test = MessageType('test')
    handled_types = (type_test,)


class TestQueueHandler(BaseQueueHandler):
    queue = TestQueue()

    consumer_logger = 'hello'
    consumers_number = 100


class TestWorker(AbstractWorker):
    async def process(self):
        self.logger.info('it is ok')
        return


MessageType.registry(TestQueue.type_test, TestQueue)

registry.register(TestQueue.type_test.name, TestWorker)


class BatchTestCase(TestCase):

    @profile
    def test(self):
        n = 10_000
        messages = TestQueueHandler.queue.type_test.bulk_create(list(range(n)))
        TestQueueHandler.queue.push_wait(messages)
        del messages

        handler = TestQueueHandler()
        handler.handle()
