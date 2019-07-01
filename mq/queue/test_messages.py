from django.test import TestCase

from mq.queue.messages import MessageType


class TestQueueMessagesGenerator(TestCase):

    def setUp(self):
        self.TYPE_1 = 'hello'
        self.generator_1 = MessageType(self.TYPE_1)

    def test_create(self):
        message_1_1 = self.generator_1.create(1)
        assert message_1_1.content == 1
        assert message_1_1.type == self.TYPE_1
        print(message_1_1.type)

        message_1_2 = self.generator_1.create(2, encode=True)
        message_1_2_expected = '{"content": 2, "object_id": null, "type": "hello", "pushed_at"'
        assert message_1_2.startswith(message_1_2_expected) == True

    def test_bulk_create(self):
        data = [
            {'content': 1, },
            {'content': 2, },
            {'content': 3, },
        ]

        messages_1_1 = self.generator_1.bulk_create(data)
        assert len(messages_1_1) == 3

        i = 1
        for m in messages_1_1:
            assert m.content == i
            assert m.type == self.TYPE_1
            assert m.object_id is None
            i += 1

    def test_bulk_create_content_list(self):
        data = [1, 2, 3]

        messages_1_1 = self.generator_1.bulk_create(data)
        assert len(messages_1_1) == 3

        i = 1
        for m in messages_1_1:
            assert m.content == i
            assert m.type == self.TYPE_1
            assert m.object_id is None
            i += 1

    def test_bulk_create_encode(self):
        data = [
            {'content': 1, },
            {'content': 2, },
            {'content': 3, },
        ]

        message_1_expected = '{"content": 1, "object_id": null, "type": "hello", "pushed_at"'

        messages_1_1 = self.generator_1.bulk_create(data, encode=True)
        assert len(messages_1_1) == 3
        assert messages_1_1[0].startswith(message_1_expected) is True
