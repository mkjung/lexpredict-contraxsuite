# Generated by Django 2.2.4 on 2019-11-13 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0051_auto_20191113_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='has_sub_tasks',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]