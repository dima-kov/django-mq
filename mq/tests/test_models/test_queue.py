from django.contrib.auth.models import User, Permission
from django.db import models
from django.test import TestCase

from mq.models import MqQueueItem


class MqQueueItemTest(TestCase):
    class QueueTest(MqQueueItem):
        permission_status_codename = 'add_logentry'
        permission_status_tuple = (10, 40)

        status = models.SmallIntegerField(
            verbose_name='Статус',
            choices=MqQueueItem.MQ_STATUS_CHOICES,
            default=MqQueueItem.CREATED,
        )

        class Meta:
            abstract = True

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username='test',
            password='test'
        )

        cls.queue = cls.QueueTest()

    def test_queue(self):
        choices = ((20, 'В черзі'), (30, 'В процесі'), (50, 'Помилка під час обробки'), (60, 'Пауза'))

        self.assertEqual(self.queue.get_status_choices(user=self.user), choices)

        self.assertEqual(self.queue.get_permitted_status_display(user=self.user), None)
        self.queue.status = 30
        self.assertEqual(self.queue.get_permitted_status_display(user=self.user), (20, 'В черзі'))
        self.queue.status = 50
        self.assertEqual(self.queue.get_permitted_status_display(user=self.user), (30, 'В процесі'))

        self.user.user_permissions.add(Permission.objects.get(name='Can change user'))
