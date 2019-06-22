import asyncio

from django.test import TestCase

from mq.mq_queue.common.cookies.manager import CookiesManager


def test_asyncio(func):
    def wrapper(self, *args, **kwargs):
        self.loop.run_until_complete(func(self, *args, **kwargs))

    return wrapper


class BaseConsumerRegistryTestCase(TestCase):
    manager = CookiesManager()

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

        self.manager.map.clear(1)
        self.manager.ngo.clear(1)
        return

    def tearDown(self):
        self.manager.map.clear(1)
        self.manager.ngo.clear(1)

    @test_asyncio
    async def test_map_load(self):
        await self.manager.load_map_cookies(3)
        assert self.manager.has_map_cookies(1) is True
        assert self.manager.has_map_cookies(2) is True
        assert self.manager.has_map_cookies(3) is True
        assert self.manager.has_map_cookies(9) is True
        assert self.manager.has_map_cookies(10) is False
        assert self.manager.has_map_cookies(11) is False

    @test_asyncio
    async def test_ngo_load(self):
        await self.manager.load_ngo_cookies(2)
        assert self.manager.has_map_cookies(1) is True
        assert self.manager.has_map_cookies(2) is True
        assert self.manager.has_map_cookies(3) is True
        assert self.manager.has_map_cookies(9) is True
        assert self.manager.has_map_cookies(10) is False

        cookies, token = self.manager.get_ngo_cookies(2)
        assert type(cookies) == dict

        assert len(token) > 0
