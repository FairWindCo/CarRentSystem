from django.db import models

from balance.models import Account


class Investor(Account):
    profit = models.FloatField(default=50,verbose_name='Коифициент распределения прибыли')
    operating_costs_percent = models.FloatField(verbose_name='Процент на операционные затраты', default=5.0)

    class Meta:
        verbose_name = 'Инвестор'
        verbose_name_plural = 'Инвесторы'


class Driver(Account):
    profit = models.FloatField(default=50, verbose_name='Процент распределения прибыли')
    fuel_compensation = models.FloatField(default=100, verbose_name='Процент компенсации топлива')
    phone = models.CharField(max_length=15, default='', null=True, blank=True)

    class Meta:
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водители'


class Counterpart(Account):
    class Meta:
        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагенты'


class InvestmentCarBalance(Account):
    create_date = models.DateField(auto_created=True)

    class Meta:
        verbose_name = 'Инвестор'
        verbose_name_plural = 'Инвесторы'
