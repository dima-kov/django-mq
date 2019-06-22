import json

from django.conf import settings

from mq.mq_queue.storage import AbstractStorageConnector


class AbstractCookiesManager(object):
    storage_key_format = None
    cookies_loader = None

    def __init__(self, storage_connector: AbstractStorageConnector):
        self.storage_connector = storage_connector
        return

    def has_cookies(self, cookies_id):
        value = self.storage_connector.get(self.storage_key(cookies_id))
        return value is not None

    def get_cookies(self, cookies_id):
        value = self.storage_connector.get(self.storage_key(cookies_id))
        return json.loads(value) if value else None

    async def load_cookies(self, cookies_id):
        cookies = await self.cookies_loader.request()
        key = self.storage_key(cookies_id)
        value = self.encode(cookies)
        self.storage_connector.set(key, value)
        self.storage_connector.expire(key, int(settings.COOKIES_STORAGE_TTL * 60))

    def clear(self, cookies_id: int):
        self.storage_connector.delete_key(self.storage_key(cookies_id))

    def storage_key(self, cookies_id: int):
        return self.storage_key_format.format(cookies_id)

    @staticmethod
    def encode(cookies: dict) -> str:
        return json.dumps(cookies)

    @staticmethod
    def decode(cookies: str) -> dict:
        return json.loads(cookies)
