import json

from mq.loaders.abstract import AbstractLoader


class ReceiptLoader(AbstractLoader):
    url = 'https://api.agroregisters.com.ua/api/cropreceipts/public/filter'

    async def load(self, entity, logger):
        return await self.request(entity, logger)

    async def request(self, number, logger):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json;charset=UTF-8',
            'ContentType': 'application/json; charset=utf-8',
            'Origin': 'https://new.agroregisters.com.ua',
            'Referer': 'https://new.agroregisters.com.ua/dashboard/public/search',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        }
        data = {
            "page": 0,
            "count": 30,
            "filterBy": {
                "status": [3],
                "action": [1, 2, 3, 4, 5, 7, 8, 9],
                "type": [1, 2]
            },
            "sortBy": "dateCreated",
            "isDesc": False,
            "fullLandRegistryNumber": number,
        }

        logger.info('Sending receipt request: {}'.format(number))

        res = await self.async_requester.POST_request(
            self.url, headers=headers, json=data, verify_ssl=False
        )
        print(res)
        return json.loads(res)

