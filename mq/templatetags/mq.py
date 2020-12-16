from django import template
from mq.models import MqError

register = template.Library()


@register.simple_tag
def mq_errors():
    return MqError.objects.filter(status=MqError.CREATED).count()
