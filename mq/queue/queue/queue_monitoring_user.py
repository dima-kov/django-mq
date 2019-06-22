from django.conf import settings

from mq.mq_queue.queue.abstract import AbstractQueueConnector
from mq.mq_queue.storage.connectors import RedisStorageConnector


class MonitoringUserQueue(AbstractQueueConnector):
    """
        MonitoringUserQueue used for intermediate allocation monitoring messages
        and for balancing many messages from different users.

        Monitoring User Queue has only `wait` list
    """
    name = settings.MONITORING_USER_QUEUE_NAME
    connector = RedisStorageConnector()

    def __init__(self):
        self.wait_list = self.name
        self.processing_list = None

    def get_queue_name(self, user_id):
        return self.wait_list.format(user_id=user_id)

    def push_wait(self, user_id, value, *values):
        return self.connector.push_list(self.get_queue_name(user_id), value, *values)

    def expire_user_queue(self, user_id):
        return self.connector.delete_key(self.get_queue_name(user_id))

    def range_user_queue(self, user_id, number):
        return self.connector.list_range(self.get_queue_name(user_id), number - 1)

    def remove_message_from_user_queue(self, user_id, message):
        return self.connector.delete_list_value(self.get_queue_name(user_id), message)
