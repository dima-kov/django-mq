from django.conf import settings

from mq.queue.abstract import AbstractQueue, AbstractQueueSystemFacade
from mq.queue.consumer_registry import ConsumerRegistry
from mq.storage.connectors.redis import RedisStorageConnector


class BaseRedisQueue(AbstractQueue):
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


class RedisQueueSystemFacade(AbstractQueueSystemFacade):
    user_queue_name = settings.MONITORING_USER_QUEUE_NAME
    monitoring_captcha_queue_name = '{}_{{stage}}'.format(settings.MONITORING_CAPTCHA_QUEUE_NAME)
    monitoring_auth_queue_name = '{}_{{stage}}'.format(settings.MONITORING_AUTHENTICATION_QUEUE_NAME)
    monitoring_number_queue_name = '{}_{{stage}}'.format(settings.MONITORING_NUMBER_QUEUE_NAME)
    number_meta_queue_name = '{}_{{stage}}'.format(settings.NUMBER_META_QUEUE_NAME)
    purpose_queue_name = '{}_{{stage}}'.format(settings.PURPOSE_QUEUE_NAME)
    connector = RedisStorageConnector()

    def push_to_user_queue(self, value, *values, user_id):
        list_name = self.user_queue_name.format(user_id=user_id)
        return self.connector.push_list(list_name, value, *values)

    def push_to_monitoring_worker(self, value, *values):
        list_name = self.monitoring_captcha_queue_name.format(stage=settings.QUEUE_WAIT_STAGE)
        return self.connector.push_list(list_name, value, *values)

    def push_to_monitoring_number_worker(self, value, *values):
        list_name = self.monitoring_number_queue_name.format(stage=settings.QUEUE_WAIT_STAGE)
        return self.connector.push_list_start(list_name, value, *values)

    def push_to_monitoring_auth_worker(self, value, *values):
        list_name = self.monitoring_auth_queue_name.format(stage=settings.QUEUE_WAIT_STAGE)
        return self.connector.push_list(list_name, value, *values)

    def push_to_monitoring_worker_start(self, value, *values):
        list_name = self.monitoring_captcha_queue_name.format(stage=settings.QUEUE_WAIT_STAGE)
        return self.connector.push_list_start(list_name, value, *values)

    def push_to_number_meta_queue(self, value, *values):
        list_name = self.number_meta_queue_name.format(stage=settings.QUEUE_WAIT_STAGE)
        return self.connector.push_list(list_name, value, *values)

    def push_to_purpose_queue(self, value, *values):
        list_name = self.purpose_queue_name.format(stage=settings.QUEUE_WAIT_STAGE)
        return self.connector.push_list(list_name, value, *values)

    def push_to_number_meta_queue_start(self, value, *values):
        list_name = self.number_meta_queue_name.format(stage=settings.QUEUE_WAIT_STAGE)
        return self.connector.push_list_start(list_name, value, *values)

    def range_user_queue(self, user_id, number):
        list_name = self.user_queue_name.format(user_id=user_id)
        return self.connector.list_range(list_name, number - 1)

    def ltrim_user_queue(self, user_id, number):
        list_name = self.user_queue_name.format(user_id=user_id)
        return self.connector.redis.ltrim(list_name, number, -1)

    def monitoring_captcha_wait_queue_len(self):
        list_name = self.monitoring_captcha_queue_name.format(stage=settings.QUEUE_WAIT_STAGE)
        return self.connector.list_len(list_name)

    def monitoring_captcha_processing_queue_len(self):
        list_name = self.monitoring_captcha_queue_name.format(stage=settings.QUEUE_PROCESSING_STAGE)
        return self.connector.list_len(list_name)

    def monitoring_number_wait_queue_len(self):
        list_name = self.monitoring_number_queue_name.format(stage=settings.QUEUE_WAIT_STAGE)
        return self.connector.list_len(list_name)

    def monitoring_number_processing_queue_len(self):
        list_name = self.monitoring_number_queue_name.format(stage=settings.QUEUE_PROCESSING_STAGE)
        return self.connector.list_len(list_name)

    def user_wait_queue_len(self, user_id):
        list_name = self.user_queue_name.format(user_id=user_id)
        return self.connector.list_len(list_name)

    def number_meta_wait_queue_len(self):
        list_name = self.number_meta_queue_name.format(stage=settings.QUEUE_WAIT_STAGE)
        return self.connector.list_len(list_name)

    def number_meta_processing_queue_len(self):
        list_name = self.number_meta_queue_name.format(stage=settings.QUEUE_PROCESSING_STAGE)
        return self.connector.list_len(list_name)
