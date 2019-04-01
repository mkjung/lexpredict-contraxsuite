# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-03-11 08:55
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_user_timezone'),
        ('document', '0124_auto_20190311_0855'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentNotificationSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=False)),
                ('event', models.CharField(choices=[('document_loaded', 'Document loaded'), ('document_deleted', 'Document deleted'), ('document_changed', 'Document changed'), ('document_assigned', 'Document assigned')], max_length=100)),
                ('recipients', models.CharField(choices=[('current_assignee', 'Current assignee'), ('specified_role', 'Specified role'), ('specified_user', 'Specified user')], max_length=100)),
                ('subject', models.CharField(blank=True, help_text='Template of the email subject in \n        Jinja2 syntax. Leave empty for using the default. The following items are passed to the context: to_user: User, event_initiator: User, documents: List[Dict[str, Any]], \n    period_start: datetime, period_end: datetime.', max_length=1024, null=True)),
                ('header', models.CharField(blank=True, help_text='Template of the header\n        in Jinja2 syntax. Leave empty for using the default. The following items are passed to the context: to_user: User, event_initiator: User, documents: List[Dict[str, Any]], \n    period_start: datetime, period_end: datetime.\n        ', max_length=2048, null=True)),
                ('generic_fields', django.contrib.postgres.fields.jsonb.JSONField(default=['status_name'], encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('document_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='document.DocumentType')),
                ('specified_role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.Role')),
                ('specified_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user_fields', models.ManyToManyField(blank=True, help_text='Fields of the documents to \n        render in the email. Should match the specified document type. Leave empty for rendering all fields.\n        ', to='document.DocumentField')),
            ],
        ),
        migrations.RenameField(
            model_name='documentdigestconfig',
            old_name='document_fields',
            new_name='user_fields',
        ),
        migrations.RemoveField(
            model_name='documentdigestconfig',
            name='template',
        ),
    ]
