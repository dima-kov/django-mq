import math
import time

from mq.queue.messages.messages import MessageDecoder
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
    max_in_queue_interval = 60 * 60  # in sec

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

    def processing_obsolete_to_wait(self):
        """
        Method pushes all obsolete queue messages from processing to wait

        Message is considered obsolete when pushed_at is more than MAX_IN_QUEUE_INTERVAL
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

    def cleanup(self):
        pass

    @staticmethod
    def unpack_values(values):
        if not isinstance(values, list):
            values = [values]

        if not values or len(values) == 0:
            return None

        return values


class Queue(AbstractQueue):
    connector: AbstractStorageConnector = None

    def __init__(self):
        super().__init__()
        if self.connector is None:
            raise ValueError('{} connector can not be None'.format(self.__class__.__name__))
        self.consumers = ConsumerRegistry(self.name, self.connector)

    def push_wait(self, values, start=False):
        values = self.unpack_values(values)
        if not values:
            return

        method = self.connector.push_list_start if start else self.connector.push_list
        return method(self.wait, *values)

    def push_processing(self, *values):
        return self.connector.push_list(self.processing, *values)

    def pop_wait_push_processing(self) -> [None, str]:
        wait_raw_message = self.connector.rpop(self.wait)
        if wait_raw_message is None:
            return

        message = MessageDecoder(wait_raw_message.decode('utf-8')).decoded()
        message.set_in_process_at()
        encoded = message.encode()
        self.push_processing(encoded)
        return encoded

    def processing_to_wait(self):
        to_wait = self.get_processing()
        if len(to_wait) > 0:
            self.push_wait(to_wait, start=True)
            self.del_processing()

    def processing_obsolete_to_wait(self):
        to_wait = self.get_processing()
        now = time.time()
        for raw_message in to_wait:
            message = MessageDecoder(raw_message).decoded()
            if not message.in_process_at:
                continue

            interval = now - message.in_process_at
            message_encoded = message.encode()
            if interval > self.max_in_queue_interval:
                self.processing_delete(raw_message)
                self.push_wait(message_encoded, start=True)

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

    def cleanup(self):
        super().cleanup()
        self.connector.delete_key(self.wait)
        self.connector.delete_key(self.processing)
        self.connector.delete_key(self.wait_capacity)
        self.consumers.cleanup()

    def get_processing(self):
        return [i.decode('utf-8') for i in self.connector.list_range(self.processing)]

    def del_processing(self):
        return self.connector.delete_key(self.processing)


class PerUserQueueMixin(Queue):
    """
    Mixin for gathering messages to queue by previous distribution per users' queues.

    :gathering_size - amount of messages to push to queue per one gathering
    @push_per_user - method to push values to user's queue
    """
    gathering_size: int = 10

    def __init__(self):
        super().__init__()
        self.__user_list = 'queue_{queue_name}_user_{{user_id}}'.format(queue_name=self.name)

    def push_per_user(self, values, user_id, start=False):
        values = self.unpack_values(values)
        method = self.connector.push_list_start if start else self.connector.push_list
        if not values:
            return

        return method(self._user_list_name(user_id), *values)

    def gather(self):
        users_id = self._get_user_ids()
        per_user, summed = self._count_per_user(users_id)

        # Refuse if number elements in queue is bigger than gathering size
        queue_size = self.len_wait()
        if queue_size >= self.gathering_size:
            print('Queue {} size is more that gathering size: {} {}'.format(
                self.__class__.__name__,
                queue_size,
                self.gathering_size,
            ))
            return
        print('Gathering per users queue: {}'.format(self.__class__.__name__))
        for user_id, user_queue_len in per_user.items():
            load_percent = math.ceil(user_queue_len / summed * 100)
            chunk = self._gathering_chunk(load_percent)
            self.push_from_user(user_id, chunk)
            print('user (id={} len={}) push {}'.format(user_id, user_queue_len, chunk))

    def len_per_user(self, user_id):
        return self.connector.list_len(self._user_list_name(user_id))

    def range_per_user(self, user_id, number=-1):
        return self.connector.list_range(self._user_list_name(user_id), number)

    def del_per_user(self, user_id, value):
        self.connector.delete_list_value(self._user_list_name(user_id), value)

    def push_from_user(self, user_id, number):
        messages = self.range_per_user(user_id, number)
        self.push_wait(messages)
        self._ltrim_per_user(user_id, number)

    def cleanup(self):
        super().cleanup()
        users_id = self._get_user_ids()
        for user_id in users_id:
            self.connector.delete_key(self._user_list_name(user_id))

    def _get_user_ids(self, **kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.filter(**kwargs).values_list('id', flat=True)

    def _ltrim_per_user(self, user_id, number=-1):
        return self.connector.ltrim(self._user_list_name(user_id), number)

    def _count_per_user(self, user_ids):
        per_user, summed = {}, 0
        for user_id in user_ids:
            user_len = self.len_per_user(user_id)
            if user_len > 0:
                per_user[user_id] = user_len
                summed += user_len
        return per_user, summed

    def _gathering_chunk(self, load_percent):
        chunk = math.ceil(load_percent / 100 * self.gathering_size)
        return chunk if chunk > 1 else 5

    def _user_list_name(self, user_id):
        return self.__user_list.format(user_id=user_id)
