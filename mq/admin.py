from django.contrib import admin

from mq.models import MqError, MqMessageType


class MqErrorAdmin(admin.ModelAdmin):
    list_display = ('raised_at', 'message_type', 'status')
    list_filter = ('message_type',)


admin.site.register(MqError, MqErrorAdmin)
admin.site.register(MqMessageType)
