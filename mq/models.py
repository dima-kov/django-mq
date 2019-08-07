from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


class MqMessageType(models.Model):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        help_text=_('Name of message type')
    )

    class Meta:
        verbose_name = _('Message Type')
        verbose_name_plural = _('Message Types')

    def __str__(self):
        return self.name


class MqError(models.Model):
    CREATED = 1
    REVIEWED = 2

    ERROR_STATUS_CHOICES = (
        (CREATED, _('Created')),
        (REVIEWED, _('Reviewed')),
    )

    UNKNOWN = None

    queue_message = models.CharField(
        max_length=1055,
        verbose_name=_('Повідомлення черги'),
        null=True, blank=True,
    )
    raised_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Викинуто о')
    )
    error_message = models.TextField(
        verbose_name=_("Трейсбек помилки")
    )
    status = models.IntegerField(
        verbose_name=_("Статус"),
        choices=ERROR_STATUS_CHOICES,
        default=CREATED,
        db_index=True,
    )
    message_type = models.ForeignKey(
        'mq.MqMessageType',
        on_delete=models.CASCADE,
        related_name='mq_errors',
        verbose_name=_('Message Type'),
        null=True, blank=True,
    )

    class Meta:
        verbose_name = _('Error')
        verbose_name_plural = _('Errors')

    def __str__(self):
        return _("Error {}").format(self.raised_at)


class MqQueueItem(models.Model):
    CREATED = 10
    IN_QUEUE = 20
    IN_PROCESS = 30
    SUCCEED = 40
    ERROR = 50

    MQ_STATUS_CHOICES = (
        (CREATED, _('Створено')),
        (IN_QUEUE, _('В черзі')),
        (IN_PROCESS, _('В процесі')),
        (SUCCEED, _('Оброблено')),
        (ERROR, _('Помилка під час обробки')),
    )
    # To use statues, just import and concatenate with custom:
    # STATUS_CHOICES = MQ_STATUS_CHOICES + (
    #   (100, _('Custom'),
    # )
    # All integers up to 100, is reserved by mq. Do no use them
    # in case of future mq updates

    in_queue_at = models.DateTimeField(
        verbose_name=_('В черзі о'),
        null=True,
        blank=True,
    )
    in_process_at = models.DateTimeField(
        verbose_name=_('Почато обробку о'),
        null=True,
        blank=True,
    )
    succeed_at = models.DateTimeField(
        verbose_name=_('Оброблено о'),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def in_process(self, commit=False):
        self.status = self.IN_PROCESS
        self.in_process_at = timezone.now()
        if commit:
            self.save(update_fields=['status', 'in_process_at'])

    def error(self, commit=False):
        self.status = self.ERROR
        if commit:
            self.save(update_fields=['status'])

    def succeed(self, commit=True):
        self.status = self.SUCCEED
        self.succeed_at = timezone.now()
        if commit:
            self.save(update_fields=['status', 'succeed_at'])

    @property
    def is_succeed(self):
        return self.status == self.SUCCEED

    @property
    def is_error(self):
        return self.status == self.ERROR
