# Generated by Django 3.2.6 on 2021-09-11 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0002_comment_reply'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='rating',
            field=models.IntegerField(default=1),
        ),
    ]
