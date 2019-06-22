import asyncio
import logging

from django.conf import settings

from apps.core.helpers import Singleton
from apps.core.models import RuCaptchaConfig
from mq.common.async_requester import AsyncRequester
from mq.common.exceptions import CaptchaBadDuplicatesError, CaptchaUnsolvableError, \
    RuCaptchaZeroBalance, CaptchaNoSlotAvailable
from mq.common.infinite_gen import ExactlyChangedInfiniteGenerator, SuspendingInfiniteGenerator
from mq.common.proxy import ProxyStorage


class CaptchaKeyGenerator(ExactlyChangedInfiniteGenerator, SuspendingInfiniteGenerator):
    suspend_after = 4

    def get_all_objects_list(self):
        return list(RuCaptchaConfig.objects.all().values_list('key', flat=True))


class RuCaptchaSolver(AsyncRequester):
    captcha_keys_gen = CaptchaKeyGenerator()
    ru_captcha_key = None
    proxy = ProxyStorage().get()

    def __init__(self, logger):
        self.logger = logger
        self.gen_next_key()

    async def solve_captcha(self):
        self.logger.info("Sending captcha in.php")
        captcha_key = self.ru_captcha_key
        self.logger.info("Using key: {}".format(captcha_key))
        try:
            captcha_id = await self.send_in_php(captcha_key)
            solved_token = await self.get_solved_token(captcha_key, captcha_id)
            self.gen_nullify()
        except (CaptchaBadDuplicatesError, CaptchaUnsolvableError):
            self.logger.info("CaptchaBadDuplicatesError or CaptchaUnsolvableError. Retry...")
            return await self.solve_captcha()
        except RuCaptchaZeroBalance:
            self.logger.info("Rucaptcha ZERO balance.")
            self.gen_next_key()
            self.logger.info("Another key is {}.".format(self.ru_captcha_key))
            return await self.solve_captcha()
        except CaptchaNoSlotAvailable:
            self.logger.info("CaptchaNoSlotAvailable. Sleep for 2 secs and retry")
            await asyncio.sleep(2)
            return await self.solve_captcha()
        return solved_token, captcha_id, captcha_key

    async def send_in_php(self, captcha_key):
        response = await self.GET_request_json(
            "http://rucaptcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}&proxy={}&json=1".format(
                captcha_key,
                settings.SITE_KEY,
                settings.CAPTCHA_PAGE_URL,
                self.proxy,
            )
        )
        self.check_captcha_response(response)
        return response['request']

    async def get_solved_token(self, captcha_key, ru_captcha_id):
        self.logger.info("Sleep for 15 seconds")
        await asyncio.sleep(15)
        self.logger.info("Sending captcha res.php")
        while True:
            response = await self.send_res_php(captcha_key, ru_captcha_id)
            self.logger.info("One try request... Response: {}".format(response['request']))

            if self.check_captcha_response(response):
                self.logger.info('Great, token is our')
                return response['request']
            await asyncio.sleep(5)

    async def send_res_php(self, captcha_key, ru_captcha_id):
        return await self.GET_request_json(
            'http://rucaptcha.com/res.php?key={}&action=get&id={}&json=1'.format(
                captcha_key,
                ru_captcha_id,
            )
        )

    @staticmethod
    def check_captcha_response(response):
        status = response['status']
        code = response['request']
        if status == 1:
            return True

        if code == 'ERROR_ZERO_BALANCE':
            raise RuCaptchaZeroBalance()

        if code == 'ERROR_CAPTCHA_UNSOLVABLE':
            raise CaptchaUnsolvableError()

        if code == 'ERROR_BAD_DUPLICATES':
            raise CaptchaBadDuplicatesError()

        if code == 'ERROR_NO_SLOT_AVAILABLE':
            raise CaptchaNoSlotAvailable()

        return False

    def gen_next_key(self):
        self.captcha_keys_gen.next(previous=self.ru_captcha_key)
        self.ru_captcha_key = self.captcha_keys_gen.current()

    def gen_nullify(self):
        self.captcha_keys_gen.nullify()


class RuCaptchaSerializer(metaclass=Singleton):

    def encode(self, solved_token, captcha_id, captcha_key):
        return '{}|{}|{}'.format(solved_token, captcha_id, captcha_key)

    def decode(self, data):
        solved_token, captcha_id, captcha_key = data.split('|')
        return solved_token, captcha_id, captcha_key


class RuCaptchaReportSender(metaclass=Singleton):
    async_requester = AsyncRequester()

    async def send_report(self, captcha_id, captcha_key):
        await self.async_requester.GET_request_json(
            'http://rucaptcha.com/res.php?key={}&action=reportbad&id={}&json=1'.format(
                captcha_key,
                captcha_id,
            )
        )


def test():
    loop = asyncio.get_event_loop()
    logger = logging.getLogger("parsing")
    solver_1 = RuCaptchaSolver(logger)
    solver_2 = RuCaptchaSolver(logger)

    loop.run_until_complete(asyncio.wait([solver_1.solve_captcha()]))
    loop.run_until_complete(asyncio.wait([solver_2.solve_captcha()]))
