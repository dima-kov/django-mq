from mq.queue.messages import MessageType
from mq.queue.queue import RedisQueue


class QueueForTest(RedisQueue):
    type_1 = MessageType('type_1')
    type_2 = MessageType('type_2')

    handled_types = (type_1, type_2)
