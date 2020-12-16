from django.utils.module_loading import import_string

from mq import settings
from mq.queue.queue import BaseQueuesFacade

QueuesFacade: BaseQueuesFacade = import_string(settings.MQ_QUEUES_FACADE_CLASS)()
