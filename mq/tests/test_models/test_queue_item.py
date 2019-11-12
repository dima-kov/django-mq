from django.contrib.auth.models import User, Permission
from django.db import models
from django.shortcuts import get_object_or_404
from django.test import TestCase

from mq.models import MqQueueItem


class MqQueueItemTest(TestCase):
    class QueueItem(MqQueueItem):
        INTERMEDIATE = 35
        NEW_CHOICE = 100

        MQ_STATUS_CHOICES = MqQueueItem.MQ_STATUS_CHOICES + (
            (NEW_CHOICE, 'New'),
            (INTERMEDIATE, 'Intermediate'),
        )
        choices_permission_code = 'auth.view_user'
        permission_required_choices = (MqQueueItem.CREATED, INTERMEDIATE, NEW_CHOICE)

        status = models.SmallIntegerField(
            verbose_name='Статус',
            choices=MQ_STATUS_CHOICES,
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

    def test_no_permission(self):
        queue_item = self.QueueItem()
        self.assertEqual(len(queue_item.MQ_STATUS_CHOICES), 8)

        expected = (
            (20, 'В черзі'), (30, 'В процесі'), (40, 'Оброблено'),
            (50, 'Помилка під час обробки'), (60, 'Пауза')
        )
        # Get choices when user has no permission
        # expected: only those choices that do no require permission
        self.assertEqual(queue_item.get_status_choices(user=self.user), expected)

        # Get permitted display when selected choice require permission
        # user is not granted and no previous status
        # Expected: None
        self.assertEqual(queue_item.get_permitted_status_display(user=self.user), None)

        # Get permitted display when choice does not require permission
        queue_item.status = MqQueueItem.IN_QUEUE
        self.assertEqual(queue_item.get_permitted_status_display(user=self.user), 'В черзі')

        # Get permitted display when choice require permission
        # user is not granted
        # Expected: previous choice display
        queue_item.status = self.QueueItem.INTERMEDIATE
        self.assertEqual(queue_item.get_permitted_status_display(user=self.user), 'В процесі')

    def test_with_permission(self):
        queue_item = self.QueueItem()

        perm = Permission.objects.get(codename='view_user')
        self.user.user_permissions.add(perm)

        # refresh from db
        user = get_object_or_404(User, id=self.user.id)

        expected = (
            (10, 'Створено'), (20, 'В черзі'), (30, 'В процесі'),
            (35, 'Intermediate'), (40, 'Оброблено'),
            (50, 'Помилка під час обробки'), (60, 'Пауза'), (100, 'New')
        )
        # Get choices when user has permission
        # expected: all choices
        self.assertEqual(queue_item.get_status_choices(user=user), expected)

        # Get permitted choice display, choice requires permission
        # Expected: choice display
        self.assertEqual(queue_item.get_permitted_status_display(user=user), 'Створено')

        # Get permitted choice display, choice does not require permission
        # Expected: choice display
        queue_item.status = MqQueueItem.IN_QUEUE
        self.assertEqual(queue_item.get_permitted_status_display(user=user), 'В черзі')

        # Get permitted choice display, choice requires permission
        # Expected: choice display
        queue_item.status = self.QueueItem.INTERMEDIATE
        self.assertEqual(queue_item.get_permitted_status_display(user=user), 'Intermediate')
