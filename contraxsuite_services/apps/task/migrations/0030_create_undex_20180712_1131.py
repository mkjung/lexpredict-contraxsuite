# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-07-12 11:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0029_task_log_extra'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX idx_task_session_id ON task_task USING BTREE ((metadata->'session_id'));",
            "DROP INDEX idx_task_session_id"),
        migrations.RunSQL(
            "CREATE INDEX idx_task_project_id ON task_task USING BTREE ((metadata->'project_id'));",
            "DROP INDEX idx_task_project_id"),
        migrations.RunSQL(
            "CREATE INDEX idx_task_file_name ON task_task USING BTREE ((metadata->'file_name'));",
            "DROP INDEX idx_task_file_name"),
    ]