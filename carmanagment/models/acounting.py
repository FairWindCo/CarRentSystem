from django.db import models

from balance.models import Account


class Investor(Account):
    profit = models.FloatField(verbose_name='Коифициент распределения прибыли')
    operating_costs_percent = models.FloatField(verbose_name='Процент на операционные затраты', default=5.0)

    class Meta:
        verbose_name = 'Инвестор'
        verbose_name_plural = 'Инвесторы'


class Driver(Account):
    profit = models.FloatField(default=0.5, verbose_name='Коифициент распределения прибыли')

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
