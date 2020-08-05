import time

from django.test import TestCase

from mq.queue.queue.tests import QueueForTest


class ObsoleteQueueTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.queue = QueueForTest()

    def tearDown(self) -> None:
        self.queue.cleanup()

    def test_not_obsolete(self):
        """
        Queue processing contains just pushed items
        After calling processing_obsolete_to_wait, any processing items
        should not be pushed into wait
        """
        n = 10
        self._assert_wait(0)
        self._assert_processing(0)

        self._push_processing(n)
        self._assert_wait(0)
        self._assert_processing(n)

        self.queue.processing_obsolete_to_wait()
        self._assert_wait(0)
        self._assert_processing(n)

    def test_obsolete(self):
        """
        Queue processing contains items pushed some time long
        After calling processing_obsolete_to_wait, all processing items
        should be pushed to wait
        """
        n = 10
        self._push_ago(n)
        self._assert_wait(0)
        self._assert_processing(n)

        self.queue.processing_obsolete_to_wait()
        self._assert_wait(n)
        self._assert_processing(0)

    def test_some_obsolete(self):
        """
        Queue processing contains items:
         - pushed some time long
         - pushed just now
        After calling processing_obsolete_to_wait, all processing items
        should be pushed to wait
        """
        ago_count = 10
        just_count = 6
        self._push_ago(ago_count)
        self._push_processing(just_count)
        self._assert_wait(0)
        self._assert_processing(just_count + ago_count)

        self.queue.processing_obsolete_to_wait()
        self._assert_wait(ago_count)
        self._assert_processing(just_count)

    def _push_processing(self, n=1, in_process_at=None):
        def one():
            t = in_process_at or time.time()
            message = self.queue.type_1.create('haha', encode=False)
            message.set_in_process_at(t)
            self.queue.push_processing(message.encode())

        [one() for _ in range(n)]

    def _push_ago(self, n):
        sec_ago = self.queue.max_in_queue_interval * 2
        test_in_process_at = time.time() - sec_ago
        self._push_processing(n, in_process_at=test_in_process_at)

    def _assert_wait(self, expected):
        self.assertEqual(self.queue.len_wait(), expected)

    def _assert_processing(self, expected):
        self.assertEqual(self.queue.len_processing(), expected)
