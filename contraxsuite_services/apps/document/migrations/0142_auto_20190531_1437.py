# Generated by Django 2.2 on 2019-05-31 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0141_auto_20190531_0709'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='generic_data',
        ),
        migrations.RemoveField(
            model_name='historicaldocument',
            name='generic_data',
        ),
    ]
