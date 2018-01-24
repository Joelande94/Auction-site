# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-06 19:13
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('YAAS', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='state',
            field=models.CharField(default='ACTIVE', max_length=15),
        ),
        migrations.AlterField(
            model_name='auction',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 6, 19, 13, 13, 853000, tzinfo=utc)),
        ),
    ]
