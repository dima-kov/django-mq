import os


def configure_logging(LOGGING, MQ_LOGGING):
    LOGGING['version'] = 1
    LOGGING['disable_existing_loggers'] = False
    LOGGING['formatters'] = {
        'mq-logger': {
            'format': '{asctime}: {name} {message}',
            'style': '{',
        }}
    LOGGING['handlers'] = {}
    LOGGING['loggers'] = {}

    directory = MQ_LOGGING['directory']
    if not os.path.exists(directory):
        os.makedirs(directory)

    handlers = MQ_LOGGING['handlers']

    if handlers:
        for handler in handlers:
            logger = handler
            logger_handler = '{}_handler'.format(logger)
            filename = os.path.join(directory, '{}.log'.format(logger))

            LOGGING['handlers'][logger_handler] = {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': filename,
                'formatter': 'mq-logger',
            }
            LOGGING['loggers'][logger] = {
                'handlers': [logger_handler],
                'level': 'DEBUG',
            }
