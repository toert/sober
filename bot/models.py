from django.db import models

TYPES_OF_AD = (
    ('buy', 'Обьявление о продаже клиенту'),
    ('sell', 'Обьявление о покупке у клиента')
)


class Ad(models.Model):

    ad_id = models.CharField(max_length=40, db_index=True, verbose_name='ID объявления')
    price_equation = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', default=0.10)
    direction = models.CharField(max_length=80, choices=TYPES_OF_AD, verbose_name='Тип обьявления')
    online_provider = models.CharField(max_length=20, verbose_name='Инструмент (QIWI и т.д.)')
    currency = models.CharField(max_length=3, verbose_name='Валюта')
    bank_name = models.CharField(max_length=80, verbose_name='Имя банка')
    min_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Минимальная цена', default=0.10)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Максимальная цена', default=0.10)
    max_amount = models.IntegerField(verbose_name='Максимальный объем')
    account_info = models.TextField(verbose_name='Информация о аккаунте')
    msg = models.TextField(verbose_name='Сообщение')
    price_limit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Предел цены (lim цена)')
    amount_limit = models.IntegerField(verbose_name='Предел объема (lim V)')
    min_amount_filter = models.IntegerField(verbose_name='V игнор')
    ad_creation_time_filter = models.DateTimeField(verbose_name='T игнор')
    step = models.IntegerField(verbose_name='Шаг цены')
    steps_quantity = models.IntegerField(verbose_name='Количество шагов')
    price_rollback = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Откат цены (откат)')
    rollback_time = models.IntegerField(verbose_name='Время отката (T откат) в секундах')
    call_frequency = models.IntegerField(verbose_name='Частота бота в секундах')
    top_fifteen = models.BooleanField(verbose_name='Топ 15')
    visible = models.BooleanField(verbose_name='Состояние объявления')

    def __str__(self):
        return '{}/{}/{}'.format(self.ad_id, self.direction, self.price_equation)


class CurrentInfo(models.Model):

    ad = models.OneToOneField(Ad, db_index=True)
    current_ad_position = models.IntegerField(verbose_name='Текущая позиция')
    current_step = models.IntegerField(verbose_name='Текущий номер шага')

    def __str__(self):
        return '{}-{}-{}'.format(self.ad.ad_id, self.current_ad_position, self.current_step)


class IllegalLogin(models.Model):

    ad = models.ForeignKey(Ad, related_name='Игнорируемые_логины', db_index=True)
    attribute_value = models.CharField(max_length=200, verbose_name='Игнорируемые логины')

    class Meta:
        verbose_name = 'Ключевое слово'
        verbose_name_plural = 'Ключевые слова'

    def __str__(self):
        return '{}-{}'.format(self.ad.ad_id, self.attribute_value)
