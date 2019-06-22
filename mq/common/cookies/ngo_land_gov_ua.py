from bs4 import BeautifulSoup
from django.conf import settings

from mq.common.async_requester import AsyncCookiesRequester
from mq.common.cookies.abstract import AbstractCookiesManager
from mq.common.proxy import ProxyStorage


class NgoLandCookiesLoader(object):
    async_cookies_requester = AsyncCookiesRequester()
    proxy_storage = ProxyStorage()
    url = 'https://ngo.land.gov.ua/uk/map/'

    async def request(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Host': 'ngo.land.gov.ua',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'uk,uk-UA;q=0.9,ru;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.3',
        }

        return await self.async_cookies_requester.get_cookies_and_html(
            self.url,
            proxy=self.proxy_storage.get(),
            headers=headers,
            verify_ssl=False,
        )


class TokenParser(object):

    @staticmethod
    def parse_token(html):
        soup = BeautifulSoup(html, 'html.parser')
        input_tag = soup.find("input", {"name": "search_cadnum[_token]"})
        if input_tag is None:
            return None

        return input_tag['value']


class NgoLandCookiesManager(AbstractCookiesManager):
    storage_key_format = settings.COOKIES_NGO_LAND_STORAGE_KEY
    cookies_loader = NgoLandCookiesLoader()

    def get_cookies(self, cookies_id):
        cookies_value = super().get_cookies(cookies_id)
        if not cookies_value:
            return None, None
        return cookies_value.get('cookies', None), cookies_value.get('token', None)

    async def load_cookies(self, cookies_id):
        html, cookies = await self.cookies_loader.request()
        key = self.storage_key(cookies_id)
        value = {'cookies': cookies, 'token': self.parse_monetary_token(html)}
        value = self.encode(value)
        self.storage_connector.set(key, value)
        self.storage_connector.expire(key, int(settings.COOKIES_STORAGE_TTL * 60))

    def parse_monetary_token(self, html):
        return TokenParser().parse_token(html)
