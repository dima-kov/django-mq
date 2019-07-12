from mq.queue.queue.abstract import Queue
from mq.queue.storage import RedisStorageConnector


class RedisQueue(Queue):
    connector = RedisStorageConnector()
