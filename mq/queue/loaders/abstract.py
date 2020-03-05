from mq.queue.common.async_requester import AsyncRequesterV2


class AbstractLoader(object):

    async def load(self, async_requester: AsyncRequesterV2, entity, logger):
        raise NotImplemented()
