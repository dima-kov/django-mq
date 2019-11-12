from django.contrib import admin

from mq.models import MqError, MqMessageType


class MqErrorAdmin(admin.ModelAdmin):
    list_display = ('raised_at', 'message_type', 'status')
    list_filter = ('message_type',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('message_type')
        return qs


admin.site.register(MqError, MqErrorAdmin)


class MqMessageTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


admin.site.register(MqMessageType, MqMessageTypeAdmin)
