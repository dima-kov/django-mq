try:
    import django
    from mq.checks import *
except ImportError:
    # pass checks if django is not installed
    pass
