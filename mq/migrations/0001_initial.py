# Generated by Django 2.2.2 on 2019-06-22 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MqError',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('queue_message', models.CharField(blank=True, max_length=1055, null=True, verbose_name='Повідомлення черги')),
                ('raised_at', models.DateTimeField(auto_now_add=True, verbose_name='Викинуто о')),
                ('error_message', models.TextField(verbose_name='Трейсбек помилки')),
                ('status', models.CharField(choices=[(1, 'Created'), (2, 'Reviewed')], db_index=True, default=1, max_length=2, verbose_name='Статус')),
                ('message_type', models.CharField(db_index=True, default='unknown', max_length=2)),
            ],
            options={
                'verbose_name': 'Error',
                'verbose_name_plural': 'Errors',
            },
        ),
    ]
