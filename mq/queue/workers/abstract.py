class AbstractWorker:
    """
        :message_content
        :message_object_id
        :logger

        :get_back_to_queue()
        Used when worker have messages to push to queue after processing all work.
        E.g.: pushing pdf link for download to queue
    """

    def __init__(self, consumer_id: int, message_content, message_object_id, logger):
        self.cid = consumer_id
        self.message_content = message_content
        self.message_object_id = message_object_id
        self.logger = logger

        # TODO: get rid of to_queue, to_next_queue, to_previous_queue,
        #  because it breaks DIP from SOLID
        self.to_queue = []
        self.to_next_queue = []
        self.to_previous_queue = []

    async def process(self):
        raise NotImplementedError()

    @classmethod
    def is_ready(cls, cid):
        return True

    @classmethod
    def is_ready_message(cls, cid):
        """Useful when consumer need to handle some message to become ready"""
        return False

    def error(self):
        """Called in queue handler when error is raised"""
        pass
