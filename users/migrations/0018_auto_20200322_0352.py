# Generated by Django 3.0.1 on 2020-03-22 03:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0017_auto_20200314_0805'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='accountIDList',
        ),
        migrations.CreateModel(
            name='CategoryCap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accountid', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=64)),
                ('amount', models.CharField(default='0', max_length=64)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]