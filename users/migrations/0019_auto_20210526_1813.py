# Generated by Django 3.0.3 on 2021-05-26 17:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20200322_0352'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categorycap',
            name='user',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='accountID',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='dateRange',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='gotAccount',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='transPerPage',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='useDateFilter',
        ),
        migrations.DeleteModel(
            name='Account',
        ),
        migrations.DeleteModel(
            name='CategoryCap',
        ),
    ]