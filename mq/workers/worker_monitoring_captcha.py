from apps.monitoring.models import ParsingItem
from mq.common.captcha_solver import RuCaptchaSolver, RuCaptchaSerializer
from mq.workers.abstract import AbstractWorker
from apps.stats.models import RuCaptchaRequest


class MonitoringCaptchaWorker(AbstractWorker):
    parsing_item = None

    async def process(self):
        self.parsing_item = ParsingItem.objects.filter(id=self.message_content).first()
        if not self.parsing_item:
            self.logger.info("Cannot find ParsingItem with id={}".format(self.message_content))
            return

        if self.parsing_item.status == ParsingItem.PAUSED:
            self.logger.info("ParsingItem (id = {}) is paused".format(self.parsing_item.id))
            return

        if self.parsing_item.status == ParsingItem.PARSED:
            self.logger.info("ParsingItem (id = {}) is already parsed".format(self.parsing_item.id))
            return

        self.logger.info("MonitoringCaptchaWorker start: {}".format(self.parsing_item.id))
        if not self.charge_money():
            self.logger.info("User has no money. Cancel")
            return

        self.parsing_item.in_process(commit=True)
        captcha_token = await self.load_captcha_token()
        self.logger.info("Captcha token == {}".format(captcha_token))

        self.to_next_queue.append(self.captcha_message(captcha_token))

    async def load_captcha_token(self):
        captcha_solver = RuCaptchaSolver(self.logger)
        captcha_token, ru_captcha_id, captcha_key = await captcha_solver.solve_captcha()
        RuCaptchaRequest.objects.create(ru_captcha_key=captcha_solver.ru_captcha_key)
        return RuCaptchaSerializer().encode(captcha_token, ru_captcha_id, captcha_key)

    def captcha_message(self, captcha_token):
        return self.message_factory.create_monitoring_number_message(self.parsing_item.id, captcha_token).encode()

    def error(self):
        self.parsing_item.error(commit=True)

    def charge_money(self):
        if self.parsing_item.funds_change:
            return True

        user = self.parsing_item.number.group.owner
        if user.get_balance() < 1:
            self.parsing_item.save_no_money()
            return False

        funds_change = user.funds_minus_parsing()
        self.parsing_item.funds_change = funds_change
        self.parsing_item.save(update_fields=['funds_change'])
        return True
