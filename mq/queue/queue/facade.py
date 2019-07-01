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


class QueueFacade(QueuePushFacade, QueueStatsFacade, QueueConsumersFacade):
    pass


class BaseQueuesFacade(object):
    """
    Class for creating several queues facade per django project.
    E.g:
    class SystemQueues(BaseQueuesFacade):
        foo = FooQueue()
        bar = BarQueue()

    Access to every queue in the system is performed through attribute SystemQueues:

    - Creating messages:
        SystemQueues().foo.foo_type.create('test message content)
    - pushing to queue:
        SystemQueues().foo.push(messages)

    Instance of BaseQueuesFacade can be stored as
    """

    def queue_by_type(self, message_type: str) -> AbstractQueue:

        for attr in self.__dir__():
            if attr is AbstractQueue:
                queue = getattr(self, attr)
                if type in queue.handled_types:
                    return queue

        raise ValueError("No queue were found for type: {}".format(message_type))
