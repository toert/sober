from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import re

TYPES_OF_AD = (
    ('buy', 'Обьявление о продаже клиенту'),
    ('sell', 'Обьявление о покупке у клиента')
)
TYPES_OF_PAYMENT_METHOD = (
    ('qiwi', 'QIWI'),
    ('transfers-with-specific-bank', 'Перевод через конкретный банк')
)
TYPES_OF_CURRENCY = (
    ('rub', 'Рубль'),
    ('usd', 'Американский доллар')
)

class LocalUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    login = models.CharField(max_length=40, db_index=True, verbose_name='Логин', default='')
    hmac_key = models.CharField(max_length=140, db_index=True, verbose_name='HMAC ключ')
    hmac_secret = models.CharField(max_length=140, verbose_name='HMAC пароль')
    proxy = models.CharField(max_length=140, verbose_name='Прокси-адрес', default='', blank=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            LocalUser.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.localuser.save()


    class Meta:
        verbose_name = 'Аккаунт LocalBitcoin'
        verbose_name_plural = 'Аккаунты LocalBitcoin'

    def get_proxies(self):
        if self.proxy:
            return {
                  "http": 'http://{}'.format(self.proxy),
                  "https": 'https://{}'.format(self.proxy),
                  "ftp": 'ftp://{}'.format(self.proxy)
                }


class Ad(models.Model):

    user = models.ForeignKey(User, related_name='ads', verbose_name='Пользователь-владелец')
    ad_id = models.CharField(max_length=40, db_index=True, verbose_name='ID объявления')
    price_equation = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', default=0.10)
    direction = models.CharField(max_length=80, choices=TYPES_OF_AD, verbose_name='Тип обьявления')
    online_provider = models.CharField(max_length=20, choices=TYPES_OF_PAYMENT_METHOD, verbose_name='Инструмент')
    currency = models.CharField(max_length=3, choices=TYPES_OF_CURRENCY, verbose_name='Валюта')
    bank_name = models.CharField(max_length=80, verbose_name='Имя банка')
    min_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Минимальная цена', default=0.10)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Максимальная цена', default=0.10)
    max_amount = models.IntegerField(verbose_name='Максимальный объем')
    account_info = models.TextField(verbose_name='Информация о аккаунте')
    msg = models.TextField(verbose_name='Сообщение')
    price_limit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Предел цены (lim цена)')
    amount_limit = models.IntegerField(verbose_name='Предел объема (lim V)')
    min_amount_filter = models.IntegerField(verbose_name='V игнор')
    #ad_creation_time_filter = models.DateTimeField(verbose_name='T игнор')
    last_online_time = models.IntegerField(verbose_name='T игнор', default=1200)
    delta_amount_filter = models.IntegerField(verbose_name='Delta V')
    phone_number = models.CharField(max_length=11, verbose_name='Номер телефона (при работе с QIWI)')
    step = models.IntegerField(verbose_name='Шаг цены')
    steps_quantity = models.IntegerField(verbose_name='Количество шагов')
    ignored_logins = models.TextField(verbose_name='Игнорируемые логины', blank=True)
    invisible_trade_ids = models.TextField(verbose_name='ID сделок-невидимок', blank=True)
    price_rollback = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Откат цены (откат)')
    rollback_time = models.IntegerField(verbose_name='Время отката (T откат) в секундах')
    start_msg = models.TextField(verbose_name='Сообщение при начале сделки', blank=True)
    finish_msg = models.TextField(verbose_name='Сообщение при завершении сделки', blank=True)
    is_top_fifteen = models.BooleanField(verbose_name='Топ 15')
    is_visible = models.BooleanField(verbose_name='Включено ли объявление?', default=False)
    is_updated = models.BooleanField(verbose_name='Обновлять ли объявление?', default=False)

    current_amount = models.IntegerField(default=1)
    current_ad_position = models.IntegerField(verbose_name='Текущая позиция', null=True)
    current_step = models.IntegerField(verbose_name='Текущий номер шага', null=True)

    class Meta:
        verbose_name = 'Обьявление'
        verbose_name_plural = 'Обьявления'

    def get_ignored_logins_as_list(self):
        list_of_logins = re.findall(r'([^, ]+)', str(self.ignored_logins))
        return list_of_logins

    def get_invisible_trade_ids_as_list(self):
        list_of_ids = re.findall(r'([^, ]+)', str(self.invisible_trade_ids))
        return list_of_ids

    def __str__(self):
        return '{}/{}/{}'.format(self.ad_id, self.direction, self.price_equation)
