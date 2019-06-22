import asyncio

from django.test import TestCase

from mq.queue.consumer_registry import ConsumerRegistry
from mq.storage.connectors.redis import RedisStorageConnector


def test_asyncio(func):
    def wrapper(self, *args, **kwargs):
        self.loop.run_until_complete(func(self, *args, **kwargs))

    return wrapper


class BaseConsumerRegistryTestCase(TestCase):
    queue = 'test_queue_hello'

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

        self.connector = RedisStorageConnector()
        self.registry = ConsumerRegistry(self.queue, self.connector)
        self.registry.cleanup()

    def tearDown(self):
        self.registry.cleanup()
        self.loop.close()


class ConsumerRegistryHelpersTestCase(BaseConsumerRegistryTestCase):
    queue = 'test_queue'

    @test_asyncio
    async def test_update_active(self):
        self.registry._update_active(1, 1)
        assert self.connector.bit_get(self.registry.consumers_active, 1) == 1

        self.registry._update_active(2, 0)
        assert self.connector.bit_get(self.registry.consumers_active, 2) == 0

        self.registry.update_active(2)
        assert self.connector.bit_get(self.registry.consumers_active, 2) == 1

        self.registry.update_inactive(2)
        assert self.connector.bit_get(self.registry.consumers_active, 2) == 0

    @test_asyncio
    async def test_update_registration(self):
        self.registry._update_register(0, 1)
        self.registry._update_register(1, 0)
        self.registry._update_register(2, 1)
        self.registry._update_register(3, 1)
        self.registry._update_register(4, 0)
        assert self.connector.bit_get(self.registry.consumers_register, 0) == 1
        assert self.connector.bit_get(self.registry.consumers_register, 1) == 0
        assert self.connector.bit_get(self.registry.consumers_register, 2) == 1
        assert self.connector.bit_get(self.registry.consumers_register, 3) == 1
        assert self.connector.bit_get(self.registry.consumers_register, 4) == 0

    @test_asyncio
    async def test_get_stopped_cids(self):
        self.registry.batch_register(5)
        self.registry._update_register(1, 0)
        self.registry._update_register(4, 0)

        stopped = self.registry._get_unregistered_cids()
        assert len(stopped) == 2
        assert stopped[0] == 1
        assert stopped[1] == 4

    @test_asyncio
    async def test_new(self):
        self.connector.set(self.registry.consumers_num, 4)

        assert self.registry._new() == 4

    @test_asyncio
    async def test_count(self):
        self.connector.set(self.registry.consumers_num, 10)
        assert self.registry._num() == 10


class ConsumerRegistryTestCase(BaseConsumerRegistryTestCase):
    queue = 'test_queue'

    @test_asyncio
    async def test_register(self):
        cid0 = self.registry.register()
        cid1 = self.registry.register()
        cid2 = self.registry.register()
        cid3 = self.registry.register()
        assert cid0 == 0
        assert cid1 == 1
        assert cid2 == 2
        assert cid3 == 3

    @test_asyncio
    async def test_batch_register_non_stopped(self):
        batch0 = self.registry.batch_register(5)
        batch1 = self.registry.batch_register(1)
        batch2 = self.registry.batch_register(3)
        batch3 = self.registry.batch_register(10)

        assert batch0[0] == 0
        assert batch0[1] == 1
        assert batch0[2] == 2
        assert batch0[3] == 3
        assert batch0[4] == 4

        assert batch1[0] == 5

        assert batch2[1] == 7

        assert batch3[0] == 9
        assert batch3[9] == 18

        assert len(batch0) == 5
        assert len(batch1) == 1
        assert len(batch2) == 3
        assert len(batch3) == 10

    @test_asyncio
    async def test_batch_register_stopped(self):
        batch0 = self.registry.batch_register(5)
        assert len(batch0) == 5

        self.registry.unregister(2)
        self.registry.unregister(3)
        assert len(self.registry._get_unregistered_cids()) == 2

        batch1 = self.registry.batch_register(2)
        assert len(batch1) == 2
        assert batch1[0] == 2
        assert batch1[1] == 3
        assert len(self.registry._get_unregistered_cids()) == 0

        self.registry.unregister(0)
        self.registry.unregister(3)
        self.registry.unregister(4)

        batch2 = self.registry.batch_register(10)
        assert batch2[0] == 0
        assert batch2[1] == 3
        assert batch2[2] == 4
        assert batch2[3] == 5
        assert batch2[9] == 11

    @test_asyncio
    async def test_count_active(self):
        cid0 = self.registry.register()
        cid1 = self.registry.register()
        cid2 = self.registry.register()
        cid3 = self.registry.register()
        assert cid0 == 0
        assert cid1 == 1
        assert cid2 == 2
        assert cid3 == 3

        self.registry.unregister(2)
        self.registry.unregister(3)

        self.registry.update_active(cid0)
        self.registry.update_active(cid1)
        self.registry.update_inactive(cid2)
        self.registry.update_active(cid3)

        assert self.registry.count_active() == 2
        assert self.registry._num() == 4
        self.registry.batch_register(100)

    @test_asyncio
    async def test_count_inactive(self):
        batch1 = self.registry.batch_register(4)
        assert len(batch1) == 4

        self.registry.update_active(0)
        self.registry.update_active(1)
        self.registry.update_inactive(2)
        self.registry.update_active(3)

        assert self.registry.count_active() == 3
        assert self.registry.count_inactive() == 1

        batch2 = self.registry.batch_register(4)
        assert len(batch2) == 4

        self.registry.update_active(4)
        self.registry.update_active(5)
        self.registry.update_inactive(6)
        self.registry.update_inactive(7)

        self.registry.unregister(6)
        self.registry.unregister(7)

        assert self.registry.count_active() == 5
        assert self.registry.count_inactive() == 1

    @test_asyncio
    async def test_count_ready(self):
        self.registry.batch_register(4)

        self.registry.update_ready(0, True)
        self.registry.update_ready(1, True)
        self.registry.update_ready(2, False)
        self.registry.update_ready(3, True)

        self.registry.unregister(2)
        self.registry.unregister(3)

        assert self.registry.count_ready() == 2
        assert self.registry._num() == 4
        self.registry.batch_register(100)

    @test_asyncio
    async def test_count_unready(self):
        self.registry.batch_register(4)

        self.registry.update_ready(0, True)
        self.registry.update_ready(1, True)
        self.registry.update_ready(2, False)
        self.registry.update_ready(3, True)

        assert self.registry.count_ready() == 3
        assert self.registry.count_unready() == 1

        self.registry.batch_register(2)

        self.registry.update_ready(4, True)
        self.registry.update_ready(5, True)
        self.registry.update_ready(6, False)
        self.registry.update_ready(7, False)

        self.registry.unregister(6)

        assert self.registry.count_ready() == 5
        assert self.registry.count_unready() == 1
