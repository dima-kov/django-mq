# Generated by Django 2.2.2 on 2019-07-15 11:52

from django.db import migrations, models
import django.db.models.deletion


def delete_all_errors(apps, schema_editor):
    MqError = apps.get_model("mq", "MqError")
    MqError.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('mq', '0005_mqmessagetype'),
    ]

    operations = [
        migrations.RunPython(delete_all_errors),
        migrations.AlterField(
            model_name='mqerror',
            name='message_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mq_errors',
                                    to='mq.MqMessageType', verbose_name='Message Type'),
        ),
    ]
