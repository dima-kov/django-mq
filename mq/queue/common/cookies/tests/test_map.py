import asyncio

from django.test import TestCase

from mq.mq_queue.common import MapLandCookiesManager
from mq.mq_queue.common import test_asyncio
from mq.mq_queue.storage import RedisStorageConnector


class BaseConsumerRegistryTestCase(TestCase):
    storage_connector = RedisStorageConnector()
    map_manager = MapLandCookiesManager(storage_connector)

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

        self.map_manager.clear(1)
        self.map_manager.clear(3)

    def tearDown(self):
        self.map_manager.clear(1)
        self.map_manager.clear(3)

    @test_asyncio
    async def test_has_cookies_empty(self):
        assert self.map_manager.has_cookies(1) is False
        assert self.map_manager.has_cookies(10) is False
        assert self.map_manager.has_cookies(40) is False

    @test_asyncio
    async def test_has_cookies_loaded(self):
        await self.map_manager.load_cookies(1)
        await self.map_manager.load_cookies(3)
        assert self.map_manager.has_cookies(1) is True
        assert self.map_manager.has_cookies(2) is False
        assert self.map_manager.has_cookies(3) is True
        assert self.map_manager.has_cookies(9) is False
        assert self.map_manager.has_cookies(10) is False
        assert self.map_manager.has_cookies(40) is False
