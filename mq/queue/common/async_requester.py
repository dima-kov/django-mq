import asyncio
from random import randint

import aiohttp
from aiohttp.http_exceptions import HttpProcessingError

REQUEST_ATTEMPTS = 3

REQUEST_RETIRES_BACKOFF = 3
REQUEST_BACKOFF_INTERVAL = 0.9


class AsyncCookiesRequester(object):

    async def get(self, url, proxy=None, **kwargs):
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
            async with session.get(url, proxy=proxy, **kwargs):
                return self.cookies(session.cookie_jar)

    async def get_cookies_and_html(self, url, proxy=None, **kwargs):
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
            async with session.get(url, proxy=proxy, **kwargs) as response:
                return await response.text(), self.cookies(session.cookie_jar)

    @staticmethod
    def cookies(jar):
        return {c.key: c.value for c in jar}


class AsyncRequestSender(object):

    @staticmethod
    async def get(url, cookies=None, **kwargs):
        async with aiohttp.ClientSession(cookies=cookies) as client:
            async with client.get(url, **kwargs) as resp:
                return await resp.text()

    @staticmethod
    async def get_json(url, cookies=None, **kwargs):
        async with aiohttp.ClientSession(cookies=cookies) as client:
            async with client.get(url, **kwargs) as resp:
                if resp.status == 403:
                    raise HttpForbidden403()
                return await resp.json()

    @staticmethod
    async def get_binary(url, cookies=None, **kwargs):
        async with aiohttp.ClientSession(cookies=cookies) as client:
            async with client.post(url, **kwargs) as resp:
                return await resp.read()

    @staticmethod
    async def post(url, cookies=None, **kwargs):
        async with aiohttp.ClientSession(cookies=cookies) as client:
            async with client.post(url, **kwargs) as resp:
                return await resp.text()

    @staticmethod
    async def post_json(url, cookies=None, **kwargs):
        async with aiohttp.ClientSession(cookies=cookies) as client:
            async with client.post(url, **kwargs) as resp:
                return await resp.json()


class AsyncRequest(object):
    sender = AsyncRequestSender()

    def __init__(self, method_name, url, data=None, cookies=None, headers=None, proxy=None, verify_ssl=False, **kwargs):
        self.method_name = method_name
        self.url = url
        self.data = data
        self.cookies = cookies
        self.headers = headers
        self.proxy = proxy
        self.verify_ssl = verify_ssl
        self.kwargs = kwargs

    async def do(self):
        return await self.method(
            self.url, data=self.data, cookies=self.cookies,
            headers=self.headers, proxy=self.proxy, verify_ssl=self.verify_ssl, **self.kwargs
        )

    @property
    def method(self):
        sender_method = getattr(self.sender, self.method_name)
        if not callable(sender_method):
            raise AttributeError('AsyncRequestSender do not support {} method'.format(self.method_name))

        return sender_method


class AsyncRequesterV2(object):

    async def get(self, url, **kwargs):
        return await self.handle(AsyncRequest('get', url, **kwargs))

    async def get_json(self, url, **kwargs):
        return await self.handle(AsyncRequest('get_json', url, **kwargs))

    async def get_binary(self, url, **kwargs):
        return await self.handle(AsyncRequest('get_binary', url, **kwargs))

    async def post(self, url, **kwargs):
        return await self.handle(AsyncRequest('post', url, **kwargs))

    async def post_json(self, url, **kwargs):
        return await self.handle(AsyncRequest('post_json', url, **kwargs))

    async def handle(self, request: AsyncRequest):
        attempt = REQUEST_ATTEMPTS
        raised_exc = None
        while attempt != 0:
            # print("[Async requester]. Attempt", attempt)
            if raised_exc:
                to_sleep = randint(1, 5)
                # print('sleep', to_sleep)
                await asyncio.sleep(to_sleep)
            try:
                return await request.do()
            except (aiohttp.ClientResponseError,
                    aiohttp.ClientOSError,
                    aiohttp.ClientConnectorError,
                    aiohttp.client_exceptions.ServerDisconnectedError,
                    aiohttp.client_exceptions.ClientOSError,
                    aiohttp.client_exceptions.ClientConnectionError,
                    aiohttp.ClientConnectionError,
                    aiohttp.ClientProxyConnectionError,
                    aiohttp.ClientHttpProxyError,
                    TimeoutError,
                    asyncio.TimeoutError,
                    ConnectionRefusedError,
                    HttpProcessingError) as exc:
                # print('Exception happened!')
                raised_exc = exc
            attempt -= 1

        raise raised_exc


class HttpForbidden403(Exception):
    pass
