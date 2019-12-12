from django.db import models
from django.test import TestCase

from mq.models import MqStatusField, MqQueueItem


class MqStatusFieldTestCase(TestCase):
    class TestModel(models.Model):
        TEST_CHOICES_A = MqQueueItem.MQ_STATUS_CHOICES + (
            (300, 'Custom choice'),
        )

        TEST_CHOICES_B = MqQueueItem.MQ_STATUS_CHOICES

        status_a = MqStatusField(
            verbose_name='Test field',
            choices=TEST_CHOICES_A,
            default=MqQueueItem.CREATED,
        )
        status_b = MqStatusField(
            verbose_name='Test field',
            choices=TEST_CHOICES_B,
            default=MqQueueItem.CREATED,
        )

        class Meta:
            abstract = True

        @property
        def status_a_setter(self):
            return self._meta.get_field('status_a').set_from_object(self)

        @property
        def status_b_setter(self):
            return self._meta.get_field('status_b').set_from_object(self)

    def test_setter(self):
        obj = self.TestModel()

        def assert_save(update_fields, *args, **kwargs):
            self.assertEqual(update_fields, ('status',))

        obj.save = assert_save

        self.assertEqual(obj.status_a, MqQueueItem.CREATED)
        obj.status_a_setter.in_process()

        self.assertEqual(obj.status_a, MqQueueItem.IN_PROCESS)
        obj.status_a_setter.error()

        self.assertEqual(obj.status_a, MqQueueItem.ERROR)
        obj.status_a_setter.succeed()

        self.assertEqual(obj.status_a, MqQueueItem.SUCCEED)

        with self.assertRaises(ValueError):
            obj.status_a_setter.check_in_choices(5)
