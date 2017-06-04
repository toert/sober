# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-04 12:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0007_localuser_proxy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ad',
            name='ad_creation_time_filter',
            field=models.IntegerField(verbose_name='T игнор в секундах'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='currency',
            field=models.CharField(choices=[('rub', 'Рубль'), ('usd', 'Американский доллар')], max_length=3, verbose_name='Валюта'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='online_provider',
            field=models.CharField(choices=[('qiwi', 'QIWI'), ('transfers-with-specific-bank', 'Перевод через конкретный банк')], max_length=20, verbose_name='Инструмент'),
        ),
        migrations.AlterField(
            model_name='localuser',
            name='proxy',
            field=models.CharField(blank=True, default='', max_length=140, verbose_name='Прокси-адрес'),
        ),
    ]
