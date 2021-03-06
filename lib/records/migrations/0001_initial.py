# Generated by Django 2.0.5 on 2018-06-18 10:34

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppRedirectState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='DropBoxUserToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accessToken', models.CharField(max_length=32768)),
            ],
        ),
        migrations.CreateModel(
            name='YellowAntRedirectState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.IntegerField()),
                ('state', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='YellowUserToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.IntegerField()),
                ('yellowant_token', models.CharField(max_length=100)),
                ('yellowant_id', models.IntegerField(default=0)),
                ('yellowant_integration_invoke_name', models.CharField(max_length=100)),
                ('yellowant_integration_id', models.IntegerField(default=0)),
                ('webhook_id', models.CharField(default='', max_length=100)),
                ('webhook_last_updated', models.DateTimeField(default=datetime.datetime.utcnow)),
            ],
        ),
        migrations.AddField(
            model_name='dropboxusertoken',
            name='user_integration',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='records.YellowUserToken'),
        ),
        migrations.AddField(
            model_name='appredirectstate',
            name='user_integration',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='records.YellowUserToken'),
        ),
    ]
