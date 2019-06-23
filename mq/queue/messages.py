import json

from django.utils import timezone

from mq.queue.queue.abstract import AbstractQueue

TYPE_NAME = "type"
CONTENT_NAME = "content"
PUSHED_AT_NAME = "pushed_at"
OBJECT_ID_NAME = "object_id"


class Message(object):

    def __init__(self, content, type, pushed_at, object_id=None):
        self.content = content
        self.type = type
        self.pushed_at = pushed_at
        self.object_id = object_id

    def encode(self):
        return json.dumps({
            CONTENT_NAME: self.content,
            OBJECT_ID_NAME: self.object_id,
            TYPE_NAME: self.type,
            PUSHED_AT_NAME: self.pushed_at,
        }, default=str)


class QueueMessagesGenerator(object):
    type: str = None

    def __init__(self, type):
        self.type = type

    def create(self, content, object_id=None, encode: bool = False):
        message = Message(content, self.type, timezone.now(), object_id)
        return message.encode() if encode else message

    def bulk_create(self, data, encode=False):
        """
            Data: list of {
                content: 1,
                object_id: 2, #  unmandatory
            }
        """

        def one(i):
            return self.create(i.get(CONTENT_NAME), i.get(OBJECT_ID_NAME), encode)

        return [one(i) for i in data]


class MessageDecoder(object):

    def __init__(self, message):
        self.raw_message = message
        self.message = self.base_decode()

    def decoded(self):
        return self.message

    def base_decode(self):
        json_message = json.loads(self.raw_message)
        return Message(
            type=json_message[TYPE_NAME],
            content=json_message[CONTENT_NAME],
            pushed_at=json_message[PUSHED_AT_NAME],
            object_id=json_message[OBJECT_ID_NAME]
        )


class MessageTypeRegistry(object):
    registry = {}

    def register(self, message_type: str, queue: type(AbstractQueue)):
        self.registry[message_type] = queue
        return


registry = MessageTypeRegistry()
