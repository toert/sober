# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-06 17:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad_id', models.CharField(db_index=True, max_length=40, verbose_name='ID объявления')),
                ('price_equation', models.DecimalField(decimal_places=2, default=0.1, max_digits=10, verbose_name='Цена')),
                ('direction', models.CharField(choices=[('buy', 'Обьявление о продаже клиенту'), ('sell', 'Обьявление о покупке у клиента')], max_length=80, verbose_name='Тип обьявления')),
                ('online_provider', models.CharField(max_length=20, verbose_name='Инструмент (QIWI и т.д.)')),
                ('currency', models.CharField(max_length=3, verbose_name='Валюта')),
                ('bank_name', models.CharField(max_length=80, verbose_name='Имя банка')),
                ('min_price', models.DecimalField(decimal_places=2, default=0.1, max_digits=10, verbose_name='Минимальная цена')),
                ('max_price', models.DecimalField(decimal_places=2, default=0.1, max_digits=10, verbose_name='Максимальная цена')),
                ('max_amount', models.IntegerField(verbose_name='Максимальный объем')),
                ('account_info', models.TextField(verbose_name='Информация о аккаунте')),
                ('msg', models.TextField(verbose_name='Сообщение')),
                ('price_limit', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Предел цены (lim цена)')),
                ('amount_limit', models.IntegerField(verbose_name='Предел объема (lim V)')),
                ('min_amount_filter', models.IntegerField(verbose_name='V игнор')),
                ('ad_creation_time_filter', models.DateTimeField(verbose_name='T игнор')),
                ('step', models.IntegerField(verbose_name='Шаг цены')),
                ('steps_quantity', models.IntegerField(verbose_name='Количество шагов')),
                ('price_rollback', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Откат цены (откат)')),
                ('rollback_time', models.IntegerField(verbose_name='Время отката (T откат) в секундах')),
                ('call_frequency', models.IntegerField(verbose_name='Частота бота в секундах')),
                ('top_fifteen', models.BooleanField(verbose_name='Топ 15')),
            ],
        ),
        migrations.CreateModel(
            name='CurrentInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_ad_position', models.IntegerField(verbose_name='Текущая позиция')),
                ('current_step', models.IntegerField(verbose_name='Текущий номер шага')),
                ('ad', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='bot.Ad')),
            ],
        ),
        migrations.CreateModel(
            name='IllegalLogin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute_value', models.CharField(max_length=200, verbose_name='Игнорируемые логины')),
                ('ad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Игнорируемые_логины', to='bot.Ad')),
            ],
            options={
                'verbose_name': 'Ключевое слово',
                'verbose_name_plural': 'Ключевые слова',
            },
        ),
    ]