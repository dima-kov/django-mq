from django.conf import settings

from apps.core.helpers import AsyncLoop
from mq.mq_queue.common.async_requester import AsyncCookiesRequester
from mq.mq_queue.common.cookies.abstract import AbstractCookiesManager
from mq.mq_queue.common.proxy import ProxyStorage


class MapLandCookiesLoader(AsyncLoop):
    async_cookies_requester = AsyncCookiesRequester()
    proxy_storage = ProxyStorage()
    url = 'https://map.land.gov.ua/kadastrova-karta/'

    async def request(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Host': 'map.land.gov.ua',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'uk,uk-UA;q=0.9,ru;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.3',
        }
        return await self.async_cookies_requester.get(
            self.url, headers=headers,
            proxy=self.proxy_storage.get(), verify_ssl=False,
        )


class MapLandCookiesManager(AbstractCookiesManager):
    storage_key_format = settings.COOKIES_MAP_LAND_STORAGE_KEY
    cookies_loader = MapLandCookiesLoader()
