# Generated by Django 3.1.2 on 2020-10-31 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookmarks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookmark',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='bookmarks', to='bookmarks.Tag'),
        ),
    ]