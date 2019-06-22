from mq.auth.auth import AuthManager
from mq.messages import MessageFactory


class AbstractWorker:
    """
        :message_content
        :message_object_id
        :logger

        :get_back_to_queue()
        Used when worker have messages to push to queue after processing all work.
        E.g.: pushing pdf link for download to queue
    """
    message_factory = MessageFactory()

    def __init__(self, consumer_id: int, message_content, message_object_id, logger):
        self.cid = consumer_id
        self.message_content = message_content
        self.message_object_id = message_object_id
        self.logger = logger

        self.to_queue = []
        self.to_next_queue = []
        self.to_previous_queue = []

    async def process(self):
        raise NotImplemented()

    @classmethod
    def is_ready(cls, cid):
        return True

    @classmethod
    def is_ready_message(cls, cid):
        return None

    def error(self):
        """Called in queue handler when error is raised"""
        pass


class AuthenticatedWorker(AbstractWorker):
    auth_manager = AuthManager()

    @classmethod
    def is_ready(cls, cid):
        print('cookies!={}, token is not None', cls.auth_manager.get_cookies(cid) != {}, cls.auth_manager.get_token(cid) is not None)
        return cls.auth_manager.get_cookies(cid) != {} and cls.auth_manager.get_token(cid) is not None

    @classmethod
    def is_currently_authenticating(cls, cid):
        return cls.auth_manager.is_authenticating(cid)
