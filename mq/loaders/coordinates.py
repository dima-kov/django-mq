import asyncio
from random import randint

from mq.common.async_requester import AsyncRequesterV2
from mq.common.proxy import ProxyStorage
from mq.loaders.abstract import AbstractLoader


class CoordinatesNotAvailableError(Exception):
    pass


class CoordinatesLoader(AbstractLoader):
    async_requester = AsyncRequesterV2()
    proxy_storage = ProxyStorage()
    url = 'https://map.land.gov.ua/kadastrova-karta/find-Parcel?cadnum={}&activeArchLayer=0'

    async def load(self, entity, cookies, logger):
        logger.info('Sending coordinates request.')
        response_str = await self.request(entity, cookies, logger)

        logger.info('Coordinates: Response: {}.'.format(response_str))
        try:
            self.check_response(response_str)
        except CoordinatesNotAvailableError:
            logger.info("CoordinatesNotAvailableError. Sleep up to 5s and retry")
            return await self.reload(entity, cookies, logger)

        return response_str

    async def reload(self, entity, cookies, logger):
        await asyncio.sleep(randint(1, 5))
        return await self.load(entity, cookies, logger)

    async def request(self, entity, cookies, logger):
        headers = {
            'Accept': 'application/json, text/javascript, /; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Referer': 'http://map.land.gov.ua/kadastrova-karta',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }

        return await self.async_requester.get(
            self.url.format(entity),
            cookies=cookies, headers=headers,
            proxy=self.proxy_storage.get(),
            verify_ssl=False,
        )

    @staticmethod
    def check_response(response):
        if 'The page you are looking for is temporarily unavailable.' in response:
            raise CoordinatesNotAvailableError()
