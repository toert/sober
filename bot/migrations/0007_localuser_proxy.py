# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-27 13:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_remove_ad_call_frequency'),
    ]

    operations = [
        migrations.AddField(
            model_name='localuser',
            name='proxy',
            field=models.CharField(default='', max_length=140, verbose_name='Прокси-адрес'),
        ),
    ]
