from django.test import TestCase

from mq.queue.messages import MessageType
from mq.queue.queue.redis import RedisQueue

message_type_name_1 = 'type_1'
message_type_name_2 = 'type_2'


class Queue1(RedisQueue):
    type_1 = MessageType(message_type_name_1)
    type_2 = MessageType(message_type_name_2)

    handled_types = (type_1, type_2)


class AbstractQueueTestCase(TestCase):

    def test_check_handled_type(self):
        q = Queue1()
        assert message_type_name_1 in q.handled_types

    def test_push(self):
        q = Queue1()
        q.push_wait([])
