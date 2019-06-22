import logging

from django.conf import settings

from mq.mq_queue.common.async_requester import AsyncRequester


class AbstractLoader(object):
    async_requester = AsyncRequester()
    main_logger = logging.getLogger(settings.MONITORING_MAIN_LOGGER_NAME)

    async def load(self, entity, logger):
        raise NotImplemented()


class AuthenticatedLoader(AbstractLoader):

    def __init__(self, cookies: dict, token: str):
        self.cookies = cookies
        self.token = token
        super().__init__()
