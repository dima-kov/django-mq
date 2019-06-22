from mq.common.async_requester import AsyncRequesterV2
from mq.common.helpers import OpenDataBotKeyStorage
from mq.loaders.abstract import AbstractLoader


class EdrpouNotAvailableError(Exception):
    pass


class DrrpEdrpouLoader(AbstractLoader):
    async_requester_2 = AsyncRequesterV2()
    key = OpenDataBotKeyStorage.open_data_bot_key
    url = 'https://opendatabot.com/api/v2/realty?apiKey={apiKey}&code={code}&role={role}&limit={limit}&offset={offset}&timeout=360'

    async def load(self, code, role, limit, offset, logger):
        logger.info('Sending opendatabot. Code {}, Role: {}, limit: {}, offset: {}'.format(code, role, limit, offset))

        response = await self.request(code, role, limit, offset, logger)
        if response['status'] != "ok":
            raise EdrpouNotAvailableError

        return response

    async def request(self, code, role, limit, offset, logger):
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        }

        url = self.url.format(apiKey=self.key, code=code, role=role, limit=limit, offset=offset)
        logger.info('EDRPOU Url: {}'.format(url))

        return await self.async_requester_2.get_json(url, headers=headers)
