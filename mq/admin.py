from django.contrib import admin

from mq.models import MqError


class MqErrorAdmin(admin.ModelAdmin):
    list_display = ('raised_at', 'message_type', 'status')


admin.site.register(MqError, MqErrorAdmin)
