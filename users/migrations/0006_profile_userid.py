# Generated by Django 3.0.1 on 2020-01-13 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20191227_1528'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='userID',
            field=models.CharField(default='null', max_length=64),
            preserve_default=False,
        ),
    ]