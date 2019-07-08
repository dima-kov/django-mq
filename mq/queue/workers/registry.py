from mq.queue.workers import AbstractWorker


class WorkersRegistry(object):
    _registry = {}  # message_type -> worker_cls

    def register(self, message_type, worker_cls):
        self._registry[message_type] = worker_cls

    def get(self, message_type: str) -> AbstractWorker:
        cls = self._registry.get(message_type)
        if cls is None:
            raise ValueError('This is {} unknown worker type. Have you registered worker?'.format(message_type))

        return cls
