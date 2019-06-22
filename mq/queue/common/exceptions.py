class TerminatedException(BaseException):
    pass


class WorkerNotAbleProcess(Exception):
    pass


class NonAuthorizedException(Exception):

    def __init__(self, html, cookies, token):
        self.html = html
        self.cookies = cookies
        self.token = token


class CsrfTokenNone(Exception):

    def __init__(self, html):
        self.html = html
        super(CsrfTokenNone, self).__init__()


class CaptchaWrongSolutionError(Exception):
    """e.land.gov.ua responded that captcha is solved wrong"""
    pass


class CaptchaUnsolvableError(Exception):
    pass


class CaptchaBadDuplicatesError(Exception):
    pass


class CaptchaNoSlotAvailable(Exception):
    pass


class NoTableInsideHtml(Exception):
    """There are no <table> on loaded page"""

    def __init__(self, html):
        message = "There are no <table> on loaded page. Html: \n{}".format(html)
        super().__init__(message)
        self.html = html


class UnknownQueueMessageType(Exception):

    def __init__(self, message_type):
        self.message = 'Unknown queue message type: {}'.format(message_type)
        super().__init__(self.message)


class RuCaptchaZeroBalance(Exception):
    pass


class UnableReachDesiredContent(Exception):

    def __init__(self, page_source, desired_content):
        self.message = 'Unable to get desired page content: {}. \nReal: {}'.format(desired_content, page_source)
        super().__init__(self.message)
