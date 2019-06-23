from mq.queue.queue.abstract import AbstractQueue


class BaseQueueFacade(object):
    queue: AbstractQueue = None


class QueuePushFacade(BaseQueueFacade):

    def push(self, values):
        return self.queue.push_wait(values)

    def push_start(self, values):
        return self.queue.push_wait(values, start=True)


class QueueStatsFacade(BaseQueueFacade):

    def len_wait(self):
        return self.queue.len_wait()

    def len_processing(self):
        return self.queue.len_processing()


class QueueConsumersFacade(BaseQueueFacade):

    def consumers_ready(self):
        return self.queue.consumers_ready()

    def consumers_active(self) -> int:
        return self.queue.consumers_active()

    def consumers_inactive(self) -> int:
        return self.queue.consumers_inactive()


class QueueMessagesFacade(BaseQueueFacade):

    def message_gen(self):
        return self.queue.message_gen


class QueueFacade(QueuePushFacade, QueueStatsFacade, QueueConsumersFacade, QueueMessagesFacade):
    pass
