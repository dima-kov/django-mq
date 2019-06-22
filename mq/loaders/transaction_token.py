from mq.common.helpers import check_non_authenticated
from mq.common.proxy import ProxyStorage
from mq.loaders.abstract import AuthenticatedLoader
from mq.parsers import TransactionTokenParser


class ELandTransactionTokenLoader(AuthenticatedLoader):
    url = 'https://e.land.gov.ua/back/cadaster/get/data/cad_num'
    # todo proxy check
    proxy = ProxyStorage().get()
    parser = TransactionTokenParser()

    async def load(self):
        html = await self.async_requester.GET_request(
            url=self.url, cookies=self.cookies,
            verify_ssl=False, proxy=self.proxy,
        )
        check_non_authenticated(html, self.cookies, self.token)
        return self.parser.parse(html)
