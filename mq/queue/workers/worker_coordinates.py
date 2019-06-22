import json
import math

from apps.monitoring.models import Number
from mq.mq_queue.common.cookies.manager import CookiesManager
from mq.mq_queue.loaders import CoordinatesLoader
from mq.mq_queue.workers import AbstractWorker


class CoordinatesWorker(AbstractWorker):
    cookies_manager = CookiesManager()
    coordinates_loader = CoordinatesLoader()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.number = Number.objects.filter(id=self.message_content).first()

    async def process(self):
        if not self.number:
            self.logger.info("Can not find Number with ID={}".format(self.message_content))
            return

        cookies = self.cookies_manager.get_map_cookies(self.cid)
        number = self.number.number
        response = await self.coordinates_loader.load(number, cookies, self.logger)

        self.logger.info("Coordinates response: {}".format(response))
        self.number.X, self.number.Y = self.process_response(response)
        self.number.save(update_fields=['X', 'Y'])
        self.logger.info("Coordinates number {} saved!".format(self.number.id))

    def process_response(self, response):
        data = json.loads(response)
        data = data['data'][0]
        if data['st_xmin'] is None:
            self.logger.info('Coordinates not found')
            return None, None

        sX = (float(data['st_xmin']) + float(data['st_xmax'])) / 2
        sY = (float(data['st_ymin']) + float(data['st_ymax'])) / 2
        a = 6378137
        pi = math.pi
        b = 6378137
        f = (a - b) / a
        e = math.sqrt(2 * f - f ** 2)
        eh = e / 2
        pih = pi / 2
        ts = math.exp(-sY / a)
        phi = pih - 2 * math.atan(ts)
        i = 0
        dphi = 1
        con = e * math.sin(phi)
        dphi = pih - 2 * math.atan(ts * ((1 - con) / (1 + con)) ** e) - phi
        phi = phi + dphi
        rLong = sX / a
        rLat = phi
        X = rLong * 180 / pi
        Y = rLat * 180 / pi
        return X, Y

    @classmethod
    def is_ready(cls, cid):
        return cls.cookies_manager.has_map_cookies(cid) and cls.cookies_manager.has_ngo_cookies(cid)

    @classmethod
    def is_ready_message(cls, cid):
        if cls.cookies_manager.is_currently_loading(cid):
            return None

        cls.cookies_manager.set_currently_loading(cid, True)
        return cls.message_factory.create_cookies_message(cid).encode()
