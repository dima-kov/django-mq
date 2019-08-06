from django.db import ProgrammingError
from django.utils import timezone

from mq.models import MqMessageType
from mq.queue.messages.messages import CONTENT_NAME, OBJECT_ID_NAME, Message


class MessageType(object):

    def __init__(self, name):
        self.name = name
        try:
            self.object, _ = MqMessageType.objects.get_or_create(name=name)
        except ProgrammingError:
            print('MqMessageType is migrated yet')
            pass

    def create(self, content, object_id=None, encode: bool = True):
        """Create a message of this type"""
        message = Message(content, self.name, timezone.now(), object_id)
        return message.encode() if encode else message

    def bulk_create(self, data, encode=True):
        """
            Create a message of this type.
            Data can be either:
            - list of {
                content: 1,
                object_id: 2, #  unmandatory
            }
            - list of just content items
        """

        def one(i):
            return one_dict(i) if type(i) == dict else one_content(i)

        def one_dict(i):
            return self.create(i.get(CONTENT_NAME), i.get(OBJECT_ID_NAME), encode=encode)

        def one_content(i):
            return self.create(i, encode=encode)

        return [one(i) for i in data]

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        return super().__eq__(other)

    def __str__(self):
        return self.name

    @classmethod
    def registry(cls, message_type, queue=None):
        return message_type_registry.register(message_type, queue=queue)


from mq.queue.messages.message_type_registry import MessageTypeRegistry

message_type_registry = MessageTypeRegistry()
