# Generated by Django 4.2.1 on 2023-08-21 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alarm_ekey_group_lock_group_lock_owner_notification_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passcode',
            name='name',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
