from django.apps import AppConfig


class MqAppConfig(AppConfig):

    def ready(self):
        from mq.facade import QueuesFacade  # noqa
