from mq.queue.queue.consumer_registry import ConsumerRegistry
from mq.queue.storage import AbstractStorageConnector


class AbstractQueue(object):
    """
    - name: queue name: used for formatting with parameter `stage`.
        E.g.: queue_number_{stage}
    - capacity: how many messages can handle one consumer. None: if no matter (by default).
    """
    name = None
    capacity = None
    consumers: ConsumerRegistry = None
    handled_types: tuple = None

    def __init__(self):
        list_name = 'queue_{}_{{stage}}'.format(self.name)
        self.wait = list_name.format(stage='wait')
        self.processing = list_name.format(stage='processing')
        self.wait_capacity = '{}_capacity'.format(self.wait)

    def get_main_handled_type(self):
        if len(self.handled_types) == 0:
            raise ValueError('{} must define at least one handled_type'.format(self.__class__.__name__))

        return self.handled_types[0]

    def push_wait(self, values, start=False):
        raise NotImplementedError()

    def pop_wait_push_processing(self):
        raise NotImplementedError()

    def processing_to_wait(self):
        """
        Pushes all values from processing into wait list
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


class Queue(AbstractQueue):
    connector: AbstractStorageConnector = None

    def __init__(self):
        super().__init__()
        if self.connector is None:
            raise ValueError('{} connector can not be None'.format(self.__class__.__name__))
        self.consumers = ConsumerRegistry(self.name, self.connector)

    def push_wait(self, values, start=False):
        value, values = self.unpack_values(values)
        if not value:
            return

        method = self.connector.push_list_start if start else self.connector.push_list
        return method(self.wait, value, *values)

    def pop_wait_push_processing(self):
        result = self.connector.rpoplpush(self.wait, self.processing)
        return result.decode('utf-8') if result else None

    def processing_to_wait(self):
        to_wait = self.get_processing()
        if len(to_wait) > 0:
            self.push_wait(to_wait, start=True)
            self.del_processing()

    def processing_delete(self, value):
        self.connector.delete_list_value(self.processing, value)

    def len_wait(self):
        return self.connector.list_len(self.wait)

    def len_processing(self):
        return self.connector.list_len(self.processing)

    def consumers_register(self, n):
        return self.consumers.batch_register(n)

    def consumer_unregister(self, consumer_id):
        return self.consumers.unregister(consumer_id)

    def consumer_active(self, consumer_id):
        return self.consumers.update_active(consumer_id)

    def consumer_inactive(self, consumer_id):
        return self.consumers.update_inactive(consumer_id)

    def consumers_active(self) -> int:
        return self.consumers.count_active()

    def consumer_ready(self, cid, ready: bool):
        return self.consumers.update_ready(cid, ready)

    def consumers_ready(self):
        return self.consumers.count_ready()

    def consumers_inactive(self) -> int:
        return self.consumers.count_inactive()

    def get_processing(self):
        return [i.decode('utf-8') for i in self.connector.list_range(self.processing)]

    def del_processing(self):
        return self.connector.delete_key(self.processing)

    @staticmethod
    def unpack_values(values):
        if not isinstance(values, list):
            values = [values]

        if len(values) == 0:
            return None, []

        return values[0], values[1:]
