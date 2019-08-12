from mq.queue.consumers.consumer import BaseQueueConsumer
from mq.queue.queue.abstract import AbstractQueue
from mq.queue.workers.abstract import AbstractWorker


class ChainStartQueueConsumer(BaseQueueConsumer):

    def __init__(self, next_queue: AbstractQueue, **kwargs):
        super().__init__(**kwargs)
        self.next_queue = next_queue

    def new_message(self):
        self.ready_checker.is_ready(self.cid)
        queue_active = self.queue.consumers_active()
        next_queue_wait = self.next_queue.len_wait()
        capacity = self.next_queue.capacity * self.next_queue.consumers_ready()

        next_queue_full = queue_active + next_queue_wait >= capacity
        return None if next_queue_full else super().new_message()

    def to_queue(self, worker: AbstractWorker):
        super().to_queue(worker)
        self.next_queue.push_wait(worker.to_next_queue, start=True)


class ChainEndQueueConsumer(BaseQueueConsumer):

    def __init__(self, previous_queue: AbstractQueue, **kwargs):
        super().__init__(**kwargs)
        self.previous_queue = previous_queue

    def to_queue(self, worker: AbstractWorker):
        super().to_queue(worker)
        self.previous_queue.push_wait(worker.to_previous_queue, start=True)
