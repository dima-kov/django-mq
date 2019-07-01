import asyncio
import logging
import signal
import traceback

from mq.models import MqError
from mq.queue.exceptions import TerminatedException, RestartMessageException, UnhandledMessageTypeException
from mq.queue.messages import MessageDecoder, Message
from mq.queue.queue.abstract import AbstractQueue
from mq.queue.workers import registry as workers_registry
from mq.queue.workers.abstract import AbstractWorker


class BaseQueueConsumer(object):
    worker_class: type(AbstractWorker) = None
    ready = False
    terminated = False
    queue: AbstractQueue = None

    def __init__(self, cid, queue: AbstractQueue, logger_name, **kwargs):
        self.cid = cid
        self.queue = queue
        self.logger = logging.getLogger(logger_name)

        if self.worker_class is None:
            self.worker_class = workers_registry.get(self.queue.get_handled_type())

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
        if message.type not in self.queue.handled_types:
            raise UnhandledMessageTypeException()

        return message

    def error(self, e, message=None, raw_message=None):
        self.logger.error('Error during processing queue item: \n{}\n'.format(e))
        type = message.type if message else MqError.UNKNOWN
        error = MqError.objects.create(
            queue_message=raw_message, error_message=traceback.format_exc(),
            message_type=type, status=MqError.CREATED,
        )

    def to_queue(self, worker: AbstractWorker):
        self.logger.info("Back to queue from worker. Messages: {}".format(worker.to_queue))
        self.queue.push_wait(worker.to_queue, start=True)


class QueueConsumer(BaseQueueConsumer):
    pass
