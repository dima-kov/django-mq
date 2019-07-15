from django.db import models
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

    UNKNOWN = 'unknown'

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
        verbose_name=_('Message Type')
    )

    class Meta:
        verbose_name = _('Error')
        verbose_name_plural = _('Errors')

    def __str__(self):
        return _("Error {}").format(self.raised_at)
