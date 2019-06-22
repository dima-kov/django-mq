from mq.queue.queue.abstract import AbstractQueue
from mq.queue.queue.consumer_registry import ConsumerRegistry
from mq.queue.storage import RedisStorageConnector


class RedisQueue(AbstractQueue):
    connector = RedisStorageConnector()

    def __init__(self):
        super().__init__()
        self.consumers = ConsumerRegistry(self.name, self.connector)

    def push_wait(self, values, start=False):
        value, values = self.unpack_values(values)
        if not value:
            return

        if start:
            return self.connector.push_list_start(self.wait_list, value, *values)

        return self.connector.push_list(self.wait_list, value, *values)

    def pop_wait_push_processing(self):
        result = self.connector.redis.rpoplpush(self.wait_list, self.processing_list)
        return result.decode('utf-8') if result else None

    def processing_to_wait(self):
        to_wait = self.get_processing()
        if len(to_wait) > 0:
            self.push_wait(to_wait, start=True)
            self.del_processing()

    def processing_delete(self, value):
        self.connector.delete_list_value(self.processing_list, value)

    def len_wait(self):
        return self.connector.list_len(self.wait_list)

    def len_processing(self):
        return self.connector.list_len(self.processing_list)

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
        return [i.decode('utf-8') for i in self.connector.list_range(self.processing_list)]

    def del_processing(self):
        return self.connector.delete_key(self.processing_list)

    @staticmethod
    def unpack_values(values):
        if not isinstance(values, list):
            values = [values]

        if len(values) == 0:
            return None, []

        return values[0], values[1:]
