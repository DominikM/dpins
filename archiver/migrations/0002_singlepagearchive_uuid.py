# Generated by Django 3.1.5 on 2021-04-29 20:26

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('archiver', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='singlepagearchive',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
