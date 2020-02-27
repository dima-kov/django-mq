from mq.queue.queue.abstract import AbstractQueue
from mq.queue.workers import registry


class ReadyChecker(object):
    """
    Class describes whether queue workers can be considered as ready
    :param check_queue: a queue for which worker ready status should be checked
    """

    def __init__(self, check_queue: AbstractQueue):
        self.queue = check_queue
        self.message_type = self.queue.get_main_handled_type()
        self.worker = registry.get(self.message_type.name)

    def is_ready(self, cid):
        """
        Method checks whether worker with cid is considered ready
        and updates its ready status into queue

        :param cid: consumer id
        :return: bool
        """
        ready = self.worker.is_ready(cid)
        self.queue.consumer_ready(cid, ready)
        return ready

    def get_unready_message(self, cid):
        """
        Method checks whether worker already returned message to become ready,
        if no returns queue message that should be handled by queue consumer to make worker active

        :param cid: consumer id
        :return: str
        """
        if not self.worker.is_ready_message(cid):
            return None

        return self.unready_message(cid)

    def unready_message(self, cid):
        """
        Method should return str with message that will be pushed into queue
        when worker is considered as unready

        Should be implemented by child classes

        :param cid: consumer id
        :return: str or None
        """
        return
