# Generated by Django 3.1.5 on 2021-04-30 21:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archiver', '0006_auto_20210430_2104'),
    ]

    operations = [
        migrations.RenameField(
            model_name='videoarchive',
            old_name='file_name',
            new_name='file_path',
        ),
    ]
