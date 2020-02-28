import logging
import time
import traceback

from mq.models import MqError
from mq.queue.consumers.ready_checker import ReadyChecker
from mq.queue.exceptions import UnhandledMessageTypeException
from mq.queue.messages import Message, message_type_registry
from mq.queue.messages.messages import MessageDecoder
from mq.queue.queue.abstract import AbstractQueue
from mq.queue.workers import registry as workers_registry
from mq.queue.workers.sync import SyncWorker


class SyncQueueConsumer(object):
    """
    :param cid: consumer id
    :param queue: queue from which consumer will consume messages
    :param logger_name: logger name
    """
    ready = False
    queue: AbstractQueue = None
    ready_checker_class = ReadyChecker

    def __init__(self, cid, queue: AbstractQueue, logger_name):
        self.cid = cid
        self.queue = queue
        self.logger = logging.getLogger(logger_name)
        self.ready_checker = self.ready_checker_class(self.queue)

    def consume(self):
        """
        Main entry point into consumer
        """
        try:
            self.consume_loop()
        except Exception as e:
            self.error(e)

        self.unregister()
        print('Consumer {} exited'.format(self.cid))

    def consume_loop(self):
        """
        Method starts consuming messages from queue
        """
        print('Consumer {} ready'.format(self.cid))
        while True:
            message = self.new_message()
            if message is None:
                self.queue.consumer_inactive(self.cid)
                time.sleep(1)
                continue

            self.queue.consumer_active(self.cid)
            self.consume_message(message)

    def new_message(self):
        """
        Method returns message for handling

        If worker is unready and unready_queue is specified during consumer init, that worker's unready message
        """
        self.ready = self.ready_checker.is_ready(self.cid)
        if self.ready:
            return self.queue.pop_wait_push_processing()

        unready_message = self.ready_checker.get_unready_message(self.cid)
        return unready_message

    def consume_message(self, raw_message):
        self.logger.info("New message from queue {}".format(raw_message))
        worker, message = None, None
        try:
            message = self.decode_message(raw_message)
            worker = self.new_worker(message)
            worker.process()
            self.to_queue(worker)

        except Exception as e:
            self.error(e, message, raw_message)
            if worker:
                worker.error()
        finally:
            self.queue.processing_delete(raw_message)

    def new_worker(self, message: Message) -> SyncWorker:
        worker_class = workers_registry.get(message.type)
        return worker_class(**self.new_worker_kwargs(message))

    def new_worker_kwargs(self, message: Message) -> {}:
        return {
            'consumer_id': self.cid,
            'message_content': message.content,
            'message_object_id': message.object_id,
            'logger': self.logger
        }

    def decode_message(self, raw_message) -> Message:
        message = MessageDecoder(raw_message).decoded()
        if message.type not in self.queue.handled_types:
            raise UnhandledMessageTypeException()

        return message

    def error(self, e, message=None, raw_message=None):
        self.logger.error('Error during processing queue item: \n{}\n'.format(e))
        message_type = message_type_registry.get(message.type) if message else MqError.UNKNOWN
        message_type = message_type.object if message_type else MqError.UNKNOWN
        MqError.objects.create(
            queue_message=raw_message, error_message=traceback.format_exc(),
            message_type=message_type, status=MqError.CREATED,
        )

    def to_queue(self, worker: SyncWorker):
        self.logger.info("Back to queue from worker. Messages: {}".format(worker.to_queue))
        self.queue.push_wait(worker.to_queue, start=True)

    def unregister(self):
        self.queue.consumer_unregister(self.cid)
