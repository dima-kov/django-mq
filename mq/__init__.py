default_add_config = 'mq.apps.MqAppConfig'

try:
    import django  # noqa
    from mq.checks import *  # noqa
except ImportError:
    # pass checks if django is not installed
    pass
