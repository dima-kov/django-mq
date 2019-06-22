from mq.queue.common.async_requester import AsyncRequesterV2


class AbstractLoader(object):
    async_requester = AsyncRequesterV2()

    async def load(self, entity, logger):
        raise NotImplemented()
