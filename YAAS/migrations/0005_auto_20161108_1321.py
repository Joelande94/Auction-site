# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-08 11:21
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('YAAS', '0004_auto_20161107_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 8, 11, 21, 1, 4000, tzinfo=utc)),
        ),
    ]
