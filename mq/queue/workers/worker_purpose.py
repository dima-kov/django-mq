from apps.monitoring.models import Number, Purpose
from mq.mq_queue.common.cookies.manager import CookiesManager
from mq.mq_queue.loaders.purpose import PurposeLoader
from mq.mq_queue.workers import AbstractWorker


def as_float(value):
    try:
        return float(value)
    except:
        return None


class PurposeWorker(AbstractWorker):
    purpose_loader = PurposeLoader()
    cookies_manager = CookiesManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.number = Number.objects.filter(id=self.message_content).first()

    async def process(self):
        if not self.number:
            self.logger.info("Can not find Number with ID={}".format(self.message_content))
            return

        self.logger.info("Purpose worker start: {}".format(self.number.id))
        cookies = self.cookies_manager.get_map_cookies(self.cid)
        response = await self.purpose_loader.load(self.number.number, cookies, self.logger)
        self.logger.info("Purpose response: {}".format(response))
        purpose = self.process_response(response)
        self.logger.info("Purpose saved: {}!".format(purpose.id))

    def process_response(self, response):
        data = response['data']
        purpose = Purpose(number=self.number)
        if not data or len(data) == 0:
            purpose.save()
            return purpose

        data = data[0]
        purpose.purpose = data['purpose']
        purpose.area = as_float(data['area'])
        purpose.save()
        return purpose
