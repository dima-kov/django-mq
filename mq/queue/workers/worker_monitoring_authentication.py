from mq.auth.auth import AuthManager
from mq.mq_queue.workers import AbstractWorker


class MonitoringAuthenticationWorker(AbstractWorker):
    auth_manager = AuthManager()

    async def process(self):
        cid = self.message_content
        self.auth_manager.authenticate(cid)
