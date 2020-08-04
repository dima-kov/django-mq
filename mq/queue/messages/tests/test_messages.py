import time
from unittest import TestCase


class MessagesTestCase(TestCase):
    def test_tim(self):
        start = 1596572378
        now = time.time()
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now)))

        print(now, start)
        print(now - start)
