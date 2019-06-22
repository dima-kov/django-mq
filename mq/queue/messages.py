import json

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
