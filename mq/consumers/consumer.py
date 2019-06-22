import asyncio
import logging
import signal
import traceback

from apps.monitoring.models import Error
from mq.common.exceptions import NonAuthorizedException, TerminatedException
from mq.messages import MessageDecoder, Message
from mq.queue.abstract import AbstractQueue
from mq.workers import registry as workers_registry
from mq.workers import AbstractWorker, AuthenticatedWorker


class RestartMessageException(Exception):
    pass


class UnhandledMessageTypeException(Exception):
    pass


class BaseQueueConsumer(object):

    @staticmethod
    def get_logger(logger_name, consumer_item):
        return logging.getLogger(logger_name.format(consumer_item=consumer_item))


class QueueConsumer(BaseQueueConsumer):
    worker_class: type(AbstractWorker) = None
    handled_type: str = None
    ready = False
    terminated = False

    def __init__(self, cid, queue: AbstractQueue, logger_name, **kwargs):
        self.cid = cid
        self.queue = queue
        self.logger = self.get_logger(logger_name, cid)

        if self.worker_class is None:
            self.worker_class = workers_registry.get(self.handled_type)

        signal.signal(signal.SIGTERM, self.terminate)

    def unregister(self):
        self.queue.consumer_unregister(self.cid)

    def terminate(self, _signo, _stack_frame):
        self.terminated = True

    async def consume(self):
        try:
            await self.consume_loop()
        except TerminatedException as e:
            raise e
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.error(e)

        print('Consumer {} exited'.format(self.cid))

    async def consume_loop(self):
        print('Consumer {} ready'.format(self.cid))
        while True:
            if self.terminated:
                raise TerminatedException

            message = self.new_message()
            if message is None:
                self.queue.consumer_inactive(self.cid)
                await asyncio.sleep(1)
                continue

            self.queue.consumer_active(self.cid)
            await self.consume_message(message)

    def update_ready(self):
        self.ready = self.worker_class.is_ready(self.cid)
        self.queue.consumer_ready(self.cid, self.ready)

    def new_message(self):
        self.update_ready()
        if self.ready:
            return self.queue.pop_wait_push_processing()

        return self.worker_class.is_ready_message(self.cid)

    async def consume_message(self, raw_message):
        self.logger.info("New message from queue {}".format(raw_message))
        worker, message = None, None
        try:
            message = self.decode_message(raw_message)
            worker = self.new_worker(message)
            await self.start_worker(worker)
            self.to_queue(worker)
        except RestartMessageException:
            self.queue.push_wait(raw_message, start=True)

        except Exception as e:
            self.error(e, message, raw_message)
            if worker:
                worker.error()
        finally:
            self.queue.processing_delete(raw_message)

    async def start_worker(self, worker: AbstractWorker):
        await worker.process()

    def new_worker(self, message: Message) -> AbstractWorker:
        return self.worker_class(**self.new_worker_kwargs(message))

    def new_worker_kwargs(self, message: Message) -> {}:
        return {
            'consumer_id': self.cid, 'message_content': message.content,
            'message_object_id': message.object_id, 'logger': self.logger
        }

    def decode_message(self, raw_message) -> Message:
        message = MessageDecoder(raw_message).decoded()
        if message.type != self.handled_type:
            raise UnhandledMessageTypeException()

        return message

    def error(self, e, message=None, raw_message=None):
        self.logger.error('Error during processing queue item: \n{}\n'.format(e))
        print(e, message)
        error = Error(queue_message=raw_message, error_message=traceback.format_exc())
        error.parse_message(message)
        error.save()

    def to_queue(self, worker: AbstractWorker):
        self.logger.info("Back to queue from worker. Messages: {}".format(worker.to_queue))
        self.queue.push_wait(worker.to_queue, start=True)


class ChainStartQueueConsumer(QueueConsumer):

    def __init__(self, next_queue: AbstractQueue, **kwargs):
        super().__init__(**kwargs)
        self.next_queue = next_queue

    def new_message(self):
        self.update_ready()
        queue_active = self.queue.consumers_active()
        next_queue_wait = self.next_queue.len_wait()
        capacity = self.next_queue.capacity * self.next_queue.consumers_ready()

        next_queue_full = queue_active + next_queue_wait >= capacity
        return None if next_queue_full else super().new_message()

    def to_queue(self, worker: AbstractWorker):
        super().to_queue(worker)
        self.next_queue.push_wait(worker.to_next_queue, start=True)


class MultipleWorkersConsumerMixin(QueueConsumer):
    """
    Consumer that can handle several message types
    Handled_type is a list, appropriate workers are dynamically
    created according to message_type

    You need to define `worker_class` attr explicitly to have possibility
    to call worker's is_ready
    """
    handled_type: (str,) = None

    def decode_message(self, raw_message):
        message = MessageDecoder(raw_message).decoded()
        if message.type not in self.handled_type:
            raise UnhandledMessageTypeException()

        return message

    def new_worker(self, message: Message) -> AbstractWorker:
        worker_class = workers_registry.get(message.type)
        return worker_class(**self.new_worker_kwargs(message))


class ChainEndQueueConsumer(QueueConsumer):

    def __init__(self, previous_queue: AbstractQueue, **kwargs):
        super().__init__(**kwargs)
        self.previous_queue = previous_queue

    def to_queue(self, worker: AbstractWorker):
        super().to_queue(worker)
        self.previous_queue.push_wait(worker.to_previous_queue, start=True)


class AuthenticatedQueueConsumer(QueueConsumer):
    """
    If there are UnAuthorizedError during handling,
    pushes message into auth queue
    """

    def __init__(self, auth_queue: AbstractQueue, **kwargs):
        super().__init__(**kwargs)
        self.auth_queue = auth_queue

    def new_message(self):
        self.update_ready()
        if not self.ready:
            self.authenticate()
            return None

        return super().new_message()

    async def start_worker(self, worker: AuthenticatedWorker):
        try:
            return await super().start_worker(worker)
        except NonAuthorizedException:
            self.logger.info('[NonAuthorizedException] Consumer. authentication')
            self.authenticate()
            self.logger.info('[NonAuthorizedException] Consumer. message pushed')

            raise RestartMessageException

    def authenticate(self):
        if self.worker_class.is_currently_authenticating(self.cid):
            # Consumer is already authenticating. No need to push new message
            return

        self.new_auth_message()

    def new_auth_message(self):
        message = self.worker_class.message_factory.create_monitoring_auth_message(self.cid)
        self.logger.info("new_auth_message {}".format(message.encode()))

        self.auth_queue.push_wait(message.encode())
        self.logger.info("new_auth_message pushed")
        self.worker_class.auth_manager.set_authenticating(self.cid)
