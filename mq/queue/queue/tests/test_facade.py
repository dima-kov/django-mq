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
        self.assertEqual(len(self.facade.all), 1)
        self.assertEqual(len(self.facade.all_dict), 1)
        self.assertTrue('queue_1' in self.facade.all_dict)

        self.assertEqual(len(self.facade.per_user), 0)
        self.assertEqual(len(self.facade.per_user_dict), 0)
