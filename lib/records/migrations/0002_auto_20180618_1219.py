# Generated by Django 2.0.5 on 2018-06-18 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dropboxusertoken',
            name='accessToken',
            field=models.CharField(default='', max_length=32768),
        ),
    ]