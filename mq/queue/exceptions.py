class TerminatedException(BaseException):
    pass


class RestartMessageException(Exception):
    pass


class UnhandledMessageTypeException(Exception):
    pass
