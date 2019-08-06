from mq.queue.messages.message_type import MessageType
from mq.queue.queue.abstract import AbstractQueue


class MessageTypeRegistry(object):

    def __init__(self):
        self.message_type_registry = {}
        self.queue_registry = {}

    def register(self, message_type: MessageType, queue: type(AbstractQueue) = None):
        self.message_type_registry[message_type.name] = message_type

        if queue:
            self.queue_registry[message_type.name] = queue

    def get(self, search_name):
        for name, message_type in self.message_type_registry.items():
            if name == search_name:
                return message_type

        return None

    def get_queue(self, search_name):
        for name, queue in self.queue_registry.items():
            if name == search_name:
                return queue

        return None
