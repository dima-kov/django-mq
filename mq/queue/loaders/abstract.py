from mq.queue.common.async_requester import AsyncRequesterV2


class AbstractLoader(object):

    def __init__(self, async_requester: AsyncRequesterV2=None):
        self.async_requester = async_requester

    async def load(self, entity, logger):
        raise NotImplemented()
