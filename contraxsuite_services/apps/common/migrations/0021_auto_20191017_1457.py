# Generated by Django 2.2.4 on 2019-10-17 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0020_auto_20191016_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menugroup',
            name='name',
            field=models.CharField(db_index=True, help_text='Menu item group (folder) name.', max_length=100),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='name',
            field=models.CharField(db_index=True, help_text='Menu item name.', max_length=100),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='url',
            field=models.CharField(db_index=True, help_text='Menu item name.', max_length=200),
        ),
    ]
