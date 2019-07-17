from django.test import TestCase

from mq.models import MqError
from mq.queue.errors.resolver import ErrorsResolver
from mq.queue.messages import MessageType, error_type_registry
from mq.queue.queue.redis import RedisQueue


class ErrorsResolverTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        class Queue1(RedisQueue):
            name = 'test_name_1'
            type_1 = MessageType('type_1')
            type_2 = MessageType('type_2')

            handled_types = (type_1, type_2)

        error_type_registry.register(Queue1.type_1, Queue1)

        cls.test_queue = Queue1()

        MqError.objects.create(
            queue_message='queue message 1',
            error_message='error message test ',
            message_type=Queue1.type_1.object
        )
        MqError.objects.create(
            queue_message='queue message 2',
            error_message='error message test 2',
            message_type=Queue1.type_1.object
        )
        MqError.objects.create(
            queue_message='queue message 3',
            error_message='error message test 3',
            message_type=Queue1.type_2.object
        )

    def test_errors_resolver(self):
        resolver = ErrorsResolver(MqError.objects.all())
        result = resolver.resolve()

        assert len(result.ignored_list) == 1
        assert len(result.succeed_list) == 1

        # Assert results succeed
        assert result.succeed_list[0][0] == self.test_queue.type_1.name
        assert result.succeed_list[0][1] == 2

        # Assert results ignored
        assert result.ignored_list[0][0] == self.test_queue.type_2.name
        assert result.ignored_list[0][1] == 1

        # Assert pushed to queue
        assert self.test_queue.len_wait() == 2

    def tearDown(self):
        self.test_queue.cleanup()
