from django.conf import settings

from mq.common.async_requester import AsyncRequesterV2
from mq.common.proxy import ProxyStorage
from mq.loaders.abstract import AbstractLoader


class MonetaryValueLoader(AbstractLoader):
    proxy = ProxyStorage()
    async_requester = AsyncRequesterV2()
    url = 'https://ngo.land.gov.ua/uk/search/searchCadnum'

    async def load(self, entity, cookies, token, logger):
        return await self.request(entity, cookies, token, logger)

    async def request(self, entity, cookies, token, logger):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Host': 'ngo.land.gov.ua',
            'Origin': 'https://ngo.land.gov.ua',
            'Referer': 'https://ngo.land.gov.ua/uk/map/',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Language': 'ru-UA,ru;q=0.9,uk-UA;q=0.8,uk;q=0.7,ru-RU;q=0.6,en-US;q=0.5,en;q=0.4',
        }
        data = {
            'search_cadnum[cad_num_search]': entity,
            'search_cadnum[_token]': token,
        }

        logger.info('Sending monetary request with:\nCookies: {}\nToken: {}\nData: {}'.format(
            cookies, token, data,
        ))

        return await self.async_requester.post(
            self.url, data=data, cookies=cookies, proxy=self.proxy.get(),
            headers=headers, verify_ssl=False,
        )


def loading_test():
    import logging
    import asyncio

    numbers = ['4610137500:02:006:0145', '4623387200:14:000:0058']
    logger = logging.getLogger(settings.NUMBER_META_LOGGER_NAME)
    tasks = [MonetaryValueLoader().load(n, logger) for n in numbers]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
