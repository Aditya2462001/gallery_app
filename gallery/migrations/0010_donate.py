# Generated by Django 3.2.6 on 2022-01-14 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0009_alter_like_authors'),
    ]

    operations = [
        migrations.CreateModel(
            name='Donate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('email', models.EmailField(max_length=254)),
                ('number', models.CharField(max_length=50)),
                ('amount', models.IntegerField(default=0)),
                ('payment_status', models.BooleanField(default=False)),
            ],
        ),
    ]
