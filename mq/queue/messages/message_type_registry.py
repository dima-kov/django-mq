from mq.queue.messages import MessageType
from mq.queue.queue.abstract import AbstractQueue


class MessageTypeRegistry(object):

    def __init__(self):
        self.registry = {}

    def register(self, message_type: MessageType, queue: type(AbstractQueue)):
        self.registry[message_type.name] = queue

    def get(self, search_name):
        for message_type, queue in self.registry.items():
            if message_type == search_name:
                return queue

        return None


message_type_registry = MessageTypeRegistry()
