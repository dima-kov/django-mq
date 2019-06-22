import aiohttp

from mq.mq_queue.common.cookies.manager import CookiesManager
from mq.mq_queue.workers import AbstractWorker


class CookiesWorker(AbstractWorker):
    cookies_manager = CookiesManager()

    async def process(self):
        self.logger.info("Cookies worker start: {}".format(self.message_content))
        cid_to_load = self.message_content

        self.logger.info("Map cookies loading ...")
        await self.load_map(cid_to_load)
        self.logger.info("Map cookies loaded")

        self.logger.info("Ngo cookies loading ...")
        await self.load_ngo(cid_to_load)
        self.logger.info("Ngo cookies loaded")

        self.cookies_manager.set_currently_loading(cid_to_load, False)
        self.logger.info("Set as loaded")

    async def load_map(self, cid):
        try:
            await self.cookies_manager.load_map_cookies(cid)
        except aiohttp.ClientConnectorError:
            self.logger.info('Map loading ClientConnectorError. Retry!')
            await self.load_map(cid)

    async def load_ngo(self, cid):
        try:
            await self.cookies_manager.load_ngo_cookies(cid)
        except aiohttp.ClientConnectorError:
            self.logger.info('Ngo loading ClientConnectorError. Retry!')
            await self.load_ngo(cid)
