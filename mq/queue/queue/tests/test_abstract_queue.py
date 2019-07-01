from django.test import TestCase

from mq.queue.messages import MessageType
from mq.queue.queue.abstract import AbstractQueue


class AbstractQueueTestCase(TestCase):

    def test_check_handled_type(self):
        message_type_name_1 = 'type_1'
        message_type_name_2 = 'type_2'

        class Queue1(AbstractQueue):
            type_1 = MessageType(message_type_name_1)
            type_2 = MessageType(message_type_name_2)

            handled_types = (type_1, type_2)

        q = Queue1()

        assert message_type_name_1 in q.handled_types
