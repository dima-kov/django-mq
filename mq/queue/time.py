try:
    from django.utils import timezone

    mq_datetime = timezone
except ImportError:
    from datetime import datetime

    mq_datetime = datetime
