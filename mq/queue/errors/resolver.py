from mq.models import MqError
from mq.queue.messages import message_type_registry


class ErrorsResolver:

    def __init__(self, qs):
        self.qs = qs.filter(status=MqError.CREATED)
        self.result = ErrorsResolverResult()

    def resolve(self):
        message_types = self.get_unique_message_types()
        for message_type in message_types:
            self.resolve_message_type(message_type)

        return self.result

    def resolve_message_type(self, message_type):
        errors_qs = self.qs.filter(message_type=message_type)

        # message type is empty
        if not message_type:
            self.ignore(errors_qs, None)
            return

        # queue not found
        queue_class = message_type_registry.get_queue(message_type.name)
        if not queue_class:
            self.ignore(errors_qs, message_type.name)
            return

        # push to queue
        self.push(errors_qs, queue_class, message_type.name)

    def ignore(self, qs, type_name):
        self.result.ignored(type_name, self._reviewed_errors_qs(qs))

    def push(self, qs, queue_class, message_type_name):
        queue = queue_class()
        messages = qs.values_list('queue_message', flat=True)
        queue.push_wait(values=list(messages), start=True)
        self.result.succeed(message_type_name, self._reviewed_errors_qs(qs))

    def get_unique_message_types(self):
        qs = self.qs.order_by().distinct('message_type')
        return [i.message_type for i in qs]

    @staticmethod
    def _reviewed_errors_qs(qs):
        return qs.update(status=MqError.REVIEWED)


class ErrorsResolverResult:

    def __init__(self):
        self.succeed_list = []
        self.ignored_list = []

    def succeed(self, message_type_name, number_resolved):
        self.succeed_list.append((message_type_name or '', number_resolved,))

    def ignored(self, message_type_name, number_resolved):
        self.ignored_list.append((message_type_name or '', number_resolved,))
