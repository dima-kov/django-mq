import json
import time

TYPE_NAME = "type"
CONTENT_NAME = "content"
PUSHED_AT_NAME = "pushed_at"
IN_PROCESS_AT_NAME = "in_process_at"
OBJECT_ID_NAME = "object_id"


class Message(object):

    def __init__(self, content, message_type, pushed_at, in_process_at=None, object_id=None):
        self.content = content
        self.type = message_type
        self.pushed_at = pushed_at
        self.object_id = object_id
        self.in_process_at = in_process_at

    def encode(self):
        return json.dumps({
            CONTENT_NAME: self.content,
            OBJECT_ID_NAME: self.object_id,
            TYPE_NAME: self.type,
            IN_PROCESS_AT_NAME: self.in_process_at,
            PUSHED_AT_NAME: self.pushed_at,
        }, default=str)

    def set_in_process_at(self, t=None):
        self.in_process_at = t or time.time()


class MessageDecoder(object):

    def __init__(self, message):
        self.raw_message = message
        self.message = self.base_decode()

    def decoded(self):
        return self.message

    def base_decode(self):
        json_message = json.loads(self.raw_message)
        return Message(
            message_type=json_message[TYPE_NAME],
            content=json_message[CONTENT_NAME],
            pushed_at=self._as_timestamp(json_message[PUSHED_AT_NAME]),
            in_process_at=self._as_timestamp(json_message[IN_PROCESS_AT_NAME]),
            object_id=json_message[OBJECT_ID_NAME]
        )

    @staticmethod
    def _as_timestamp(raw_time: [int, float, str]):
        """
        Raw time is considered to be a int or float or numeric str representing epoch
        """
        try:
            return int(raw_time)
        except (ValueError, TypeError):
            return
