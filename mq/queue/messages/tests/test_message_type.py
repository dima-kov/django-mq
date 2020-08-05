from django.test import TestCase

from mq.queue.messages import MessageType


class TestMessageType(TestCase):

    def setUp(self):
        self.TYPE_1 = 'hello'
        self.message_type_1 = MessageType(self.TYPE_1)

    def test_create(self):
        message_1_1 = self.message_type_1.create(1, encode=False)
        assert message_1_1.content == 1
        assert message_1_1.type == self.TYPE_1

        message_1_2 = self.message_type_1.create(2)
        message_1_2_expected = '{"content": 2, "object_id": null, "type": "hello",'
        self.assertTrue(message_1_2.startswith(message_1_2_expected))

    def test_bulk_create(self):
        data = [
            {'content': 1, },
            {'content': 2, },
            {'content': 3, },
        ]

        messages_1_1 = self.message_type_1.bulk_create(data, encode=False)
        assert len(messages_1_1) == 3

        i = 1
        for m in messages_1_1:
            assert m.content == i
            assert m.type == self.TYPE_1
            assert m.object_id is None
            i += 1

    def test_bulk_create_content_list(self):
        data = [1, 2, 3]

        messages_1_1 = self.message_type_1.bulk_create(data, encode=False)
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

        message_1_expected = '{"content": 1, "object_id": null, "type": "hello", '

        messages_1_1 = self.message_type_1.bulk_create(data, encode=True)
        assert len(messages_1_1) == 3
        self.assertTrue(messages_1_1[0].startswith(message_1_expected))
