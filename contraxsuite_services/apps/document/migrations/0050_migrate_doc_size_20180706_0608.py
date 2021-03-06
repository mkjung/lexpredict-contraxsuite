# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-07-06 06:08
from __future__ import unicode_literals

import os

from django.db import migrations
from django.conf import settings


def migrate_doc_size(apps, schema_editor):
    Document = apps.get_model('document', 'Document')
    for doc in Document.objects.all():
        try:
            file_size = os.path.getsize(os.path.join(
                '/data/media',
                settings.FILEBROWSER_DOCUMENTS_DIRECTORY,
                doc.source_path))
            doc.file_size = file_size
            doc.save()
        except:
            pass

class Migration(migrations.Migration):

    dependencies = [
        ('document', '0049_auto_20180706_0553'),
    ]

    operations = [
        migrations.RunPython(migrate_doc_size),
    ]
