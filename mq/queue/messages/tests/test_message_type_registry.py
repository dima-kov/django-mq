from django.test import TestCase

from mq.queue.messages import MessageType
from mq.queue.messages.message_type_registry import ErrorTypeRegistry
from mq.queue.queue.abstract import AbstractQueue


class Queue1(AbstractQueue):
    type_1 = MessageType('type_1')
    type_2 = MessageType('type_2')
    type_3 = MessageType('type_3')

    handled_types = (type_1, type_2, type_3)


class TestMessageTypeRegistry(TestCase):

    def setUp(self):
        self.q = Queue1()

    def test_registry(self):
        registry = ErrorTypeRegistry()
        registry.register(Queue1.type_1, Queue1)
        registry.register(Queue1.type_2, Queue1)
        registry.register(Queue1.type_3, Queue1, handle_errors=False)

        assert registry.get_queue(Queue1.type_1.name) == Queue1
        assert registry.get_queue(Queue1.type_2.name) == Queue1
        assert registry.get_queue(Queue1.type_3.name) is None
        assert registry.get_queue('random') is None
