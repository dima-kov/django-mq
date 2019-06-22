from mq.common.exceptions import CaptchaWrongSolutionError
from mq.common.helpers import check_non_authenticated
from mq.common.proxy import ProxyStorage
from mq.loaders.abstract import AuthenticatedLoader


class NumberLoader(AuthenticatedLoader):
    proxy = ProxyStorage().get()
    url = 'https://e.land.gov.ua/back/cadaster/get/data/cad_num'

    async def load(self, number: str, transaction_token: str, captcha_token: str, logger):
        logger.info("Using proxy: {}".format(self.proxy))
        logger.info("Number authenticated_load, entity: {}".format(number))
        return await self.e_land_page_request(number, captcha_token, transaction_token, logger)

    async def e_land_page_request(self, number, captcha_token, transaction_token, logger):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': "uk-UA,uk;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6",
            'Cache-Control': 'no-cache',
            "Content-Type": "application/x-www-form-urlencoded",
            'Host': 'e.land.gov.ua',
            "Origin": "https://e.land.gov.ua",
            'Pragma': 'no-cache',
            'Referer': 'https://e.land.gov.ua/back/cadaster/get/data/cad_num',
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/67.0.3396.99 Safari/537.36",
        }

        data = {
            'cadastre_find_by_cadnum[cadNum]': number,
            'g-recaptcha-response': captcha_token,
            'cadastre_find_by_cadnum[_token]': self.token,
            'cadastre_find_by_cadnum[token]': transaction_token,
        }
        logger.info('data={}'.format(data))
        logger.info('cookies={}'.format(self.cookies))

        response = await self.async_requester.POST_request(
            self.url, cookies=self.cookies,
            data=data, headers=headers,
            verify_ssl=False, proxy=self.proxy,
        )
        self.check_wrong_captcha(response)
        check_non_authenticated(response, self.cookies, self.token)
        return response

    @staticmethod
    def check_wrong_captcha(html):
        if 'Капчу введено невірно' in html:
            raise CaptchaWrongSolutionError()
