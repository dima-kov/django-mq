from django.test import TestCase

from mq.queue.messages import MessageType
from mq.queue.queue.redis import RedisQueue
from mq.queue.workers import AbstractWorker


class Queue1(RedisQueue):
    name = 'dummy'

    type_dummy = MessageType('dummy')
    handled_types = (type_dummy,)


queue_1 = Queue1()


class Worker1(AbstractWorker):

    async def process(self):
        print('Some job')
        return

    @classmethod
    def is_ready(cls, cid):
        return False

    @classmethod
    def is_ready_message(cls, cid):
        if cls.cookies_manager.is_currently_loading(cid):
            return False

        cls.cookies_manager.set_currently_loading(cid, True)
        return True


class TestConsumer(TestCase):

    def setUp(self):
        self.TYPE_1 = 'hello'
        self.message_type_1 = MessageType(self.TYPE_1)
