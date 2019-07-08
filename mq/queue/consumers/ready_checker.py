from mq.queue.queue.abstract import AbstractQueue
from mq.queue.workers import registry


class ReadyChecker(object):

    def __init__(self, queue: AbstractQueue):
        self.queue = queue
        self.message_type = self.queue.get_main_handled_type()
        self.worker = registry.get(self.message_type.name)

    def is_ready(self, cid):
        ready = self.worker.is_ready(cid)
        self.queue.consumer_ready(cid, ready)
        return ready

    def is_ready_message(self, cid):
        if not self.worker.is_ready_message(cid):
            return None

        return self.unready_message(cid)

    def unready_message(self, cid):
        return None
