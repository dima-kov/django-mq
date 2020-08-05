from django.test import TestCase

from mq.queue.messages.messages import MessageDecoder
from mq.queue.queue.tests import QueueForTest


class PushQueueTestCase(TestCase):
    """
    Test queue push, pop, pop_wait_push_processing
    """

    @classmethod
    def setUpTestData(cls):
        cls.queue = QueueForTest()

    def tearDown(self) -> None:
        self.queue.cleanup()

    def test_pop_wait_push_processing(self):
        """
        Test whether in_process_at is set during pop_wait_push_processing
        """
        self._push_wait()

        raw_message = self.queue.pop_wait_push_processing()
        self._assert_wait(0)
        self._assert_processing(1)

        message = MessageDecoder(raw_message).decoded()
        self.assertIsNotNone(message.in_process_at)

    def _push_wait(self, n=1):
        messages = self.queue.type_1.bulk_create(['nerd' for _ in range(n)])
        self.queue.push_wait(messages)

    def _assert_wait(self, expected):
        self.assertEqual(self.queue.len_wait(), expected)

    def _assert_processing(self, expected):
        self.assertEqual(self.queue.len_processing(), expected)
