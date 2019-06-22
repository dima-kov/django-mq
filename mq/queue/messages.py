import json

from django.utils import timezone

TYPE_NAME = "type"
CONTENT_NAME = "content"
PUSHED_AT_NAME = "pushed_at"
OBJECT_ID_NAME = "object_id"

MONITORING_CAPTCHA_MESSAGE_TYPE = 'monitoring_captcha'
MONITORING_NUMBER_MESSAGE_TYPE = 'monitoring_number'
MONITORING_AUTHENTICATION_MESSAGE_TYPE = 'monitoring_auth'

COORDINATES_MESSAGE_TYPE = 'coordinates'
MONETARY_MESSAGE_TYPE = 'monetary'
AGRO_RECEIPT_TYPE = 'agro_receipt'
PURPOSE_MESSAGE_TYPE = 'purpose'
NUMBER_META_COOKIES = 'number_meta_cookies'

DRRP_COORDINATES_MESSAGE_TYPE = 'drrp_coordinates'
DRRP_EDRPOU_MESSAGE_TYPE = 'drrp_edrpou'


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


class MessageFactory(object):

    @staticmethod
    def create_monitoring_number_message(parsing_item_id, captcha_token):
        return Message(captcha_token, MONITORING_NUMBER_MESSAGE_TYPE, timezone.now(), parsing_item_id)

    @staticmethod
    def create_monitoring_captcha_message(parsing_item_id):
        return Message(parsing_item_id, MONITORING_CAPTCHA_MESSAGE_TYPE, timezone.now())

    @staticmethod
    def create_monitoring_auth_message(consumer_id):
        return Message(consumer_id, MONITORING_AUTHENTICATION_MESSAGE_TYPE, timezone.now())

    @staticmethod
    def create_coordinates_message(number_id):
        return Message(number_id, COORDINATES_MESSAGE_TYPE, timezone.now())

    @staticmethod
    def create_monetary_message(number_id):
        return Message(number_id, MONETARY_MESSAGE_TYPE, timezone.now())

    @staticmethod
    def create_receipt_message(parsing_item_id):
        return Message(parsing_item_id, AGRO_RECEIPT_TYPE, timezone.now())

    @staticmethod
    def create_purpose_message(number_id):
        return Message(number_id, PURPOSE_MESSAGE_TYPE, timezone.now())

    @staticmethod
    def create_cookies_message(consumer_id):
        return Message(consumer_id, NUMBER_META_COOKIES, timezone.now())

    @staticmethod
    def create_drrp_coordinates_message(number_id):
        return Message(number_id, DRRP_COORDINATES_MESSAGE_TYPE, timezone.now())

    @staticmethod
    def create_drrp_edrpou_message(number_id):
        return Message(number_id, DRRP_EDRPOU_MESSAGE_TYPE, timezone.now())


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
