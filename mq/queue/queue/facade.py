from mq.queue.queue.abstract import AbstractQueue, PerUserQueueMixin


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

    def cleanup_queues(self):
        for queue in self.all:
            queue.cleanup()

    @property
    def all(self):
        return [value for _, value in self.all_dict.items()]

    @property
    def all_dict(self):
        class_attrs = vars(self.__class__).items()
        return {name: value for name, value in class_attrs if isinstance(value, AbstractQueue)}

    @property
    def per_user(self):
        return [value for _, value in self.per_user_dict.items()]

    @property
    def per_user_dict(self):
        return {name: value for name, value in self.all_dict.items() if isinstance(value, PerUserQueueMixin)}
