import json
import re

from apps.monitoring.models import Number
from mq.mq_queue.common.cookies.manager import CookiesManager
from mq.mq_queue.loaders.monetary_value import MonetaryValueLoader
from mq.mq_queue.workers import AbstractWorker


class MonetaryValueNotLoaded(Exception):

    def __init__(self, message, response):
        super().__init__(message)
        self.response = response

    def __str__(self):
        return '{}: {}'.format(super().__str__(), self.response)


class MonetaryValueWorker(AbstractWorker):
    monetary_loader = MonetaryValueLoader()
    cookies_manager = CookiesManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.number = Number.objects.filter(id=self.message_content).first()

    async def process(self):
        if not self.number:
            self.logger.info("Can not find Number with ID={}".format(self.message_content))
            return

        cookies, token = self.cookies_manager.get_ngo_cookies(self.cid)
        response_str = await self.monetary_loader.load(self.number.number, cookies, token, self.logger)
        self.logger.info('Monetary value response: \n{}'.format(response_str))
        response = json.loads(response_str)

        if response.get('success') is not True:
            raise MonetaryValueNotLoaded('Monetary value failed to load', response)
        if response['data'] == '':
            return

        self.number.ownership = response['data']['ownership']
        self.number.square = response['data']['area']
        self.number.aim = response['data']['purpose']

        self.process_response(response)
        self.number.save(update_fields=['monetary_valuation', 'ownership', 'square', 'aim'])
        self.logger.info("Monetary Number {} saved!".format(self.message_content))

    def process_response(self, response):
        monetary_result = self.find_monetary(str(response['evaluation']))
        self.logger.info("Monetary result: {}".format(monetary_result))
        if monetary_result:
            self.number.monetary_valuation = float(monetary_result)

    def find_monetary(self, html):
        regex_str = r"<strong id = 'parcel_evaluation' >(\d*.\d*)<\/strong>"
        monetary = re.search(regex_str, html)
        if monetary:
            return self.regex_only_money(monetary.group())
        return

    def regex_only_money(self, html):
        regex_str = r"([0-9]{1,20}.[0-9]{1,20})"
        monetary = re.search(regex_str, html)
        if monetary:
            return monetary.group()
        return
