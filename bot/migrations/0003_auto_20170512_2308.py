# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-12 20:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_auto_20170512_2240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currentinfo',
            name='current_ad_position',
            field=models.IntegerField(null=True, verbose_name='Текущая позиция'),
        ),
        migrations.AlterField(
            model_name='currentinfo',
            name='current_step',
            field=models.IntegerField(null=True, verbose_name='Текущий номер шага'),
        ),
    ]
