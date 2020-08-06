from django.test import TestCase

from mq.queue.queue.facade import BaseQueuesFacade
from mq.queue.queue.tests import QueueForTest


class FacadeForTest(BaseQueuesFacade):
    queue_1 = QueueForTest()


class FacadeTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.facade = FacadeForTest()

    def test(self):
        queues = self.facade._queues
        self.assertEqual(len(queues), 1)

        per_user_queues = self.facade._per_user_queues
        self.assertEqual(len(per_user_queues), 0)
