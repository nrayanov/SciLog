# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-04 10:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('protocols', '0008_result_datetime_created'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='result',
            options={'ordering': ['-datetime_created', 'owner']},
        ),
    ]