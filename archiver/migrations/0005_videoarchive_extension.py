# Generated by Django 3.1.5 on 2021-04-30 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archiver', '0004_auto_20210429_2201'),
    ]

    operations = [
        migrations.AddField(
            model_name='videoarchive',
            name='extension',
            field=models.CharField(default='', max_length=4),
            preserve_default=False,
        ),
    ]
