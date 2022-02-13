from django.db import models

from balance.models import Account
from .rent_price import RentTerms


class Investor(Account):
    profit = models.FloatField(default=50, verbose_name='Коифициент распределения прибыли')
    operating_costs_percent = models.FloatField(verbose_name='Процент на операционные затраты', default=5.0)
    limit_to_manager_confirm = models.FloatField(default=10000,
                                                 verbose_name='Сумма от которой требуется подверждение менеджера')
    limit_to_investor_confirm = models.FloatField(default=-1,
                                                 verbose_name='Сумма от которой требуется подверждение менеджера')

    class Meta:
        verbose_name = 'Инвестор'
        verbose_name_plural = 'Инвесторы'


class Driver(Account):
    default_terms = models.ForeignKey(RentTerms, on_delete=models.CASCADE, verbose_name='Условия по умолчанию',
                                      blank=True, null=True, related_name='drivers_terms')
    phone = models.CharField(max_length=15, default='', null=True, blank=True, verbose_name='Телефон')

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
