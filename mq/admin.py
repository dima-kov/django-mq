from django.contrib import admin, messages
from django.utils.translation import gettext as _

from mq.models import MqError, MqMessageType
from mq.queue.errors import ErrorsResolver


def action_resolve(modeladmin, request, queryset):
    resolver = ErrorsResolver(qs=queryset)
    result = resolver.resolve()
    for ignored in result.ignored_list:
        messages.warning(request, _("{} Ігноровано: {}").format(ignored[0].title(), ignored[1]))

    for succeed in result.succeed_list:
        messages.success(request, _("{} В чергу: {}").format(succeed[0].title(), succeed[1]))


action_resolve.short_description = "Resolve errors into queue"


class MqErrorAdmin(admin.ModelAdmin):
    list_display = ('raised_at', 'message_type', 'status')
    list_filter = ('message_type',)
    actions = [action_resolve]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('message_type')
        return qs


admin.site.register(MqError, MqErrorAdmin)


class MqMessageTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


admin.site.register(MqMessageType, MqMessageTypeAdmin)
