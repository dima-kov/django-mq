import asyncio
import logging
import signal
import traceback

from mq.models import MqError
from mq.queue.consumers.ready_checker import ReadyChecker
from mq.queue.exceptions import TerminatedException, UnhandledMessageTypeException
from mq.queue.messages import Message, message_type_registry
from mq.queue.messages.messages import MessageDecoder
from mq.queue.queue.abstract import AbstractQueue
from mq.queue.workers import registry as workers_registry
from mq.queue.workers.abstract import AbstractWorker


class BaseQueueConsumer(object):
    """
    :param cid: consumer id
    :param queue: queue from which consumer will consume messages
    :param logger_name: logger name
    :param unready_queue: a queue in which unready message will be pushed
        if the worker is not ready. If not specified, unready message is returned
        into a consumer from ready checker and is being handled by it without pushing into queue
    """
    ready = False
    queue: AbstractQueue = None
    ready_checker_class = ReadyChecker

    def __init__(self, cid, queue: AbstractQueue, logger_name, unready_queue: AbstractQueue = None):
        self.cid = cid
        self.queue = queue
        self.logger = logging.getLogger(logger_name)
        self.ready_checker = self.get_ready_checker()
        self.unready_queue = unready_queue

        signal.signal(signal.SIGTERM, self.terminate)
        signal.signal(signal.SIGINT, self.terminate)

    def unregister(self):
        self.queue.consumer_unregister(self.cid)

    def terminate(self, _signo, _stack_frame):
        raise TerminatedException

    async def consume(self):
        """
        Main entry point into consumer
        """
        try:
            await self.consume_loop()
        except TerminatedException as e:
            print(f'Consumer {self.cid}: TerminatedException')
            raise e
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.error(e)

        self.unregister()
        print('Consumer {} exited'.format(self.cid))

    async def consume_loop(self):
        """
        Method starts consuming messages from queue
        """
        print('Consumer {} ready'.format(self.cid))
        while True:
            message = await self.new_message()
            if message is None:
                self.queue.consumer_inactive(self.cid)
                await asyncio.sleep(1)
                continue

            self.queue.consumer_active(self.cid)
            await self.consume_message(message)

    async def new_message(self):
        """
        Method returns message for handling

        Method checks whether worker is ready for work, if yes: pops first message from queue and returns it.

        If worker is unready and unready_queue is specified during consumer init, that worker's unready message
        will be pushed into this unread queue, but self consumer will receive nothing

        If no unready_queue specified unready message from worker will be returned
        """
        self.ready = await self.ready_checker.is_ready(self.cid)
        if self.ready:
            return self.queue.pop_wait_push_processing()

        unready_message = await self.ready_checker.get_unready_message(self.cid)
        if self.unready_queue:
            self.unready_queue.push_wait(unready_message, start=True)
            return

        return unready_message

    async def consume_message(self, raw_message):
        self.logger.info("New message from queue {}".format(raw_message))
        worker, message = None, None
        try:
            message = self.decode_message(raw_message)
            worker = self.new_worker(message)
            await worker.process()
            self.to_queue(worker)

        except Exception as e:
            self.error(e, message, raw_message)
            if worker:
                worker.error()
        finally:
            self.queue.processing_delete(raw_message)

    def new_worker(self, message: Message) -> AbstractWorker:
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

    def to_queue(self, worker: AbstractWorker):
        self.logger.info("Back to queue from worker. Messages: {}".format(worker.to_queue))
        self.queue.push_wait(worker.to_queue, start=True)

    def get_ready_checker(self):
        return self.ready_checker_class(self.queue)


class QueueConsumer(BaseQueueConsumer):
    pass
