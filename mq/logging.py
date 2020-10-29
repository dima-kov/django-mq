import os

FORMATTER_NAME = 'mq-logger'

FORMATTERS = {
    FORMATTER_NAME: {
        'format': '{asctime}: {name} {message}',
        'style': '{',
    }
}


def configure_logging(LOGGING: dict, MQ_LOGGING_LOGGERS: list, MQ_LOGGING_DIRECTORY: str):
    LOGGING['version'] = 1
    LOGGING['disable_existing_loggers'] = False
    formatters = LOGGING.get('formatters', {})
    formatters.update(FORMATTERS)
    LOGGING['formatters'] = formatters

    LOGGING['handlers'] = LOGGING.get('handlers', {})
    LOGGING['loggers'] = LOGGING.get('loggers', {})

    if not os.path.exists(MQ_LOGGING_DIRECTORY):
        os.makedirs(MQ_LOGGING_DIRECTORY)

    for name in MQ_LOGGING_LOGGERS:
        handler, logger = handler_and_logger(name, MQ_LOGGING_DIRECTORY)
        LOGGING['handlers'].update(handler)
        LOGGING['loggers'].update(logger)


def handler_and_logger(name, logging_directory):
    handler = '{}_handler'.format(name)
    filename = os.path.join(logging_directory, '{}.log'.format(name))

    handlers = {
        handler: {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': filename,
            'formatter': FORMATTER_NAME,
        }
    }
    loggers = {
        name: {
            'handlers': [handler],
            'level': 'DEBUG',
        }
    }
    return handlers, loggers
