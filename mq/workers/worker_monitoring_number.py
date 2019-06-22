import asyncio
from random import randint

from apps.core.helpers import PdfProcessor
from apps.monitoring.models import ParsingItem
from mq.auth.auth import AuthManager
from mq.common.captcha_solver import RuCaptchaSerializer, RuCaptchaReportSender
from mq.common.exceptions import NonAuthorizedException, NoTableInsideHtml
from mq.loaders.pdf import PdfLoader
from mq.loaders.transaction_token import ELandTransactionTokenLoader
from mq.parsers import NumberParser
from mq.loaders.numbers import NumberLoader
from mq.workers.abstract import AbstractWorker, AuthenticatedWorker
from apps.stats.models import RuCaptchaWrongSolution

import io


class MonitoringNumberWorker(AuthenticatedWorker, AbstractWorker):
    auth_manager = AuthManager()
    parsing = None

    async def process(self):
        self.logger.info(
            "Message_content = {}, message_object_id = {}".format(self.message_content, self.message_object_id)
        )
        time_to_sleep = randint(1, 5)
        self.logger.info('Sleep {}s'.format(time_to_sleep))
        await asyncio.sleep(time_to_sleep)

        self.parsing = ParsingItem.objects.filter(id=self.message_object_id).first()
        if not self.parsing:
            self.logger.info("Cannot find ParsingItem with id={}".format(self.message_object_id))
            return

        if self.parsing.status == ParsingItem.PARSED:
            self.logger.info("ParsingItem (id = {}) is already parsed".format(self.parsing.id))
            return

        cookies, token = self.auth_manager.get(self.cid)

        try:
            transaction_token = await ELandTransactionTokenLoader(cookies, token).load()
            if not transaction_token:
                raise ValueError("Can't load transaction token")
            self.logger.info('transaction_token = {}'.format(transaction_token))

            captcha_token, captcha_id, captcha_key = RuCaptchaSerializer().decode(self.message_content)

            table_html = await NumberLoader(cookies=cookies, token=token).load(
                self.parsing.number.number, transaction_token,
                captcha_token, self.logger
            )
            pdf_link = self.parse(table_html)

        except NonAuthorizedException as e:
            self.logger.info('[NonAuthorizedException] Worker. Nullifying auth')
            self.auth_manager.nullify(self.cid)
            self.logger.info('[NonAuthorizedException] Worker. auth now: {} token={}'.format(
                self.auth_manager.get_cookies(self.cid),
                self.auth_manager.get_token(self.cid),
            ))
            self.logger.info('[NonAuthorizedException] Raise exception again')
            raise e
        except NoTableInsideHtml:
            self.logger.info('!!! NoTableInsideHtml !!!')
            self.wrong_captcha(captcha_id, captcha_key)
            return

        if 'The server returned a "403 Forbidden"' in table_html:
            self.error_403()
            return

        if self.parsing.number.group.save_pdf and pdf_link:
            pdf_worker = PdfSubWorker(self.parsing, cookies=cookies, token=token, logger=self.logger)
            await pdf_worker.process(pdf_link)

        self.done()

    def error(self):
        self.parsing.error(commit=True)

    def done(self):
        self.parsing.parsed()

    def error_403(self):
        self.logger.info("403 Forbidden error!!!")
        self.to_previous_queue.append(
            self.message_factory.create_monitoring_captcha_message(self.parsing.id).encode()
        )

    def wrong_captcha(self, captcha_id, captcha_key):
        RuCaptchaWrongSolution.objects.create(ru_captcha_id=captcha_id, ru_captcha_key=captcha_key)
        self.logger.info('Wrong captcha {}'.format(captcha_id))
        RuCaptchaReportSender().send_report(captcha_id, captcha_key)
        self.logger.info('Error report to captcha sent!')

        self.to_previous_queue.append(
            self.message_factory.create_monitoring_captcha_message(self.parsing.id).encode()
        )

    def parse(self, table_html):
        self.logger.info("Number worker loader done. Parsing!")
        parser = NumberParser(self.parsing, table_html, self.logger)
        parser.parse()
        return parser.parse_pdf_link()


class PdfSubWorker(object):
    processor = PdfProcessor()

    def __init__(self, parsing, cookies, token, logger):
        self.parsing = parsing
        self.cookies = cookies
        self.token = token
        self.logger = logger

    async def process(self, pdf_link):
        file_binary_loaded = await PdfLoader(self.cookies, self.token).load(pdf_link, self.logger)
        self.logger.info("File downloaded {}".format(self.pdf_filename()))

        temp = io.BytesIO()
        temp.write(file_binary_loaded)
        file = self.processor.file_hide_name(temp)
        self.parsing.pdf.save(self.pdf_filename(), file)
        self.logger.info("File saved")

    def pdf_filename(self):
        return '{}.pdf'.format(self.parsing.number.number)
