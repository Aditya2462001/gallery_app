# Generated by Django 3.2.6 on 2021-11-15 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0007_auto_20211115_1159'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='like',
            name='like',
        ),
        migrations.AddField(
            model_name='like',
            name='authors',
            field=models.ManyToManyField(null=True, to='gallery.Author'),
        ),
    ]
