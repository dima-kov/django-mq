from django.conf import settings

from mq.mq_queue.common import MapLandCookiesManager
from mq.mq_queue.common.cookies.ngo_land_gov_ua import NgoLandCookiesManager
from mq.mq_queue.storage import RedisStorageConnector


class CookiesManager(object):

    def __init__(self):
        self.storage_connector = RedisStorageConnector()
        self.map = MapLandCookiesManager(self.storage_connector)
        self.ngo = NgoLandCookiesManager(self.storage_connector)

    def has_map_cookies(self, cid):
        return self.map.has_cookies(self._cookies_id(cid))

    def has_ngo_cookies(self, cid):
        return self.ngo.has_cookies(self._cookies_id(cid))

    def get_map_cookies(self, cid):
        return self.map.get_cookies(self._cookies_id(cid))

    def get_ngo_cookies(self, cid):
        return self.ngo.get_cookies(self._cookies_id(cid))

    async def load_map_cookies(self, cid):
        return await self.map.load_cookies(self._cookies_id(cid))

    async def load_ngo_cookies(self, cid):
        return await self.ngo.load_cookies(self._cookies_id(cid))

    def is_currently_loading(self, cid):
        id = self._cookies_id(cid)
        key = settings.CONSUMERS_PER_ONE_COOKIE_STATE.format(id)
        return bool(self.storage_connector.get_int(key))

    def set_currently_loading(self, cid, value: bool):
        id = self._cookies_id(cid)
        key = settings.CONSUMERS_PER_ONE_COOKIE_STATE.format(id)
        self.storage_connector.set(key, int(value))

    @staticmethod
    def _cookies_id(cid: int):
        """
        Get cookies storage ID by cid:
        1-9 > 0
        10-19 > 1
        20-29 > 2
        """
        return cid // settings.CONSUMERS_PER_ONE_COOKIES_SET
