from mq.queue.workers.abstract import AbstractWorker
from mq.queue.workers.registry import WorkersRegistry

registry = WorkersRegistry()

__all__ = [AbstractWorker]
