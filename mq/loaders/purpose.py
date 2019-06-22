from django.conf import settings

from mq.common.proxy import ProxyStorage
from mq.loaders.abstract import AbstractLoader


class PurposeLoader(AbstractLoader):
    proxy = ProxyStorage()
    url = 'https://map.land.gov.ua/kadastrova-karta/get-parcel-Info?koatuu={}&zone={}&quartal={}&parcel={}'

    async def load(self, cad_number, cookies, logger):
        coatuu, zone, kwartal, dil = cad_number.split(':')
        response = await self.request(coatuu, zone, kwartal, dil, cookies, logger)
        logger.info('Response: {}'.format(response))
        return response

    async def request(self, coatuu, zone, kwartal, dil, cookies, logger):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'uk,uk-UA;q=0.9,ru;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Host': 'map.land.gov.ua',
            'Referer': 'https://map.land.gov.ua/kadastrova-karta',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }

        logger.info('Sending purpose request: {}:{}:{}:{}'.format(coatuu, zone, kwartal, dil))

        url = self.url.format(coatuu, zone, kwartal, dil)
        return await self.async_requester.GET_request_json(
            url, cookies=cookies, proxy=self.proxy.get(),
            headers=headers, verify_ssl=False,
        )


def loading_test():
    import logging
    import asyncio

    numbers = ['4610137500:02:006:0145', '4623387200:14:000:0058']
    logger = logging.getLogger(settings.NUMBER_META_LOGGER_NAME)
    tasks = [PurposeLoader().load(n, {}, logger) for n in numbers]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
