# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-02 20:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0008_noncompete_provision'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='has_noncompete',
            field=models.BooleanField(default=False),
        ),
    ]
