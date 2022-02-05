from balance.models import CashBox
from car_management.models import Counterpart
from django.db import models


class TaxiOperator(Counterpart):
    cash_profit = models.FloatField(default=17, verbose_name='Коэффициент прибили с поезди оператора (нал)')
    profit = models.FloatField(default=17, verbose_name='Коэффициент прибили с поезди оператора (без нал)')
    bank_interest = models.FloatField(default=2.5, verbose_name='Комиссия за перевод (без нал)')
    tax = models.FloatField(default=0, verbose_name='Налог на прибыль')
    cash_box = models.ForeignKey(CashBox, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Оператор такси'
        verbose_name_plural = 'Оператор такси'
