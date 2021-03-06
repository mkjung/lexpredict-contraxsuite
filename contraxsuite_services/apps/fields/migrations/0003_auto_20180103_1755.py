# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-03 17:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fields', '0002_auto_20180103_1738'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentAnnotationTag',
            fields=[
                ('id', models.CharField(max_length=256, primary_key=True, serialize=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='documentannotation',
            name='tag',
        ),
        migrations.AddField(
            model_name='documentannotation',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='documentannotation',
            name='tags',
            field=models.ManyToManyField(to='fields.DocumentAnnotationTag'),
        ),
    ]
