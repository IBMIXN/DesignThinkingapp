# Generated by Django 3.0.1 on 2020-03-13 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20200313_0546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='gotAccount',
            field=models.CharField(default='0', max_length=1),
        ),
    ]
