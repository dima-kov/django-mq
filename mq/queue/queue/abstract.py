from mq.queue.queue.consumer_registry import ConsumerRegistry


class AbstractQueue(object):
    """
    - name: queue name: used for formatting with parameter `stage`.
        E.g.: number_queue_{stage}
    - capacity: how many messages can handle one consumer. None: if no matter (by default).
    """
    name = None
    capacity = None
    consumers: ConsumerRegistry = None
    handled_type: str = None

    def __init__(self):
        list_name = '{}_{{stage}}'.format(self.name)
        self.wait_list = list_name.format(stage='wait')
        self.processing_list = list_name.format(stage='processing')
        self.wait_list_capacity = '{}_capacity'.format(self.wait_list)

    def get_handled_type(self):
        return self.handled_type

    def push_wait(self, values, start=False):
        raise NotImplementedError()

    def pop_wait_push_processing(self):
        raise NotImplementedError()

    def processing_to_wait(self):
        """
        Pushes all values from processing into wait list
        :param start: if True, all values will be pushed to the start of wait
        """
        raise NotImplementedError()

    def processing_delete(self, value):
        """Delete value from processing list"""
        raise NotImplementedError()

    def len_wait(self):
        raise NotImplementedError()

    def len_processing(self):
        raise NotImplementedError()

    def consumers_register(self, n):
        raise NotImplementedError()

    def consumer_unregister(self, cid):
        raise NotImplementedError()

    def consumer_active(self, cid):
        raise NotImplementedError()

    def consumer_inactive(self, cid):
        raise NotImplementedError()

    def consumer_ready(self, cid, ready: bool):
        raise NotImplementedError()

    def consumers_ready(self):
        raise NotImplementedError()

    def consumers_active(self) -> int:
        raise NotImplementedError()

    def consumers_inactive(self) -> int:
        raise NotImplementedError()


class MultipleTypesAbstractQueue(AbstractQueue):
    handled_types: tuple = None

    def get_handled_type(self):
        if len(self.handled_type) == 0:
            raise ValueError('{} must specify at least one handled_type'.format(self.__class__.__name__))

        return self.handled_types[0]
