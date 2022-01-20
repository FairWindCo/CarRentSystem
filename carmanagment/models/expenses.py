from audit_log.models import CreatingUserField
from django.db import models

from balance.models import Account, Transaction
from carmanagment.models import Counterpart


class ExpensesTypes(models.Model):
    class ExpensesTypesClassify(models.IntegerChoices):
        CAR_EXPENSE = 1, 'Затраты на автомобиль'
        CAPITAL_CAR_EXPENSE = 2, 'Капитальные затраты на автомобиль'
        CRASH_CAR_EXPENSE = 3, 'Страховые случаи'
        OTHER = 100, 'Прочее'

    name = models.CharField(max_length=250)
    type_class = models.PositiveSmallIntegerField(choices=ExpensesTypesClassify.choices,
                                                  verbose_name='Класс затрат',
                                                  default=ExpensesTypesClassify.OTHER)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Тип затрат'
        verbose_name_plural = 'Типы затрат'


class Expenses(models.Model):
    date_mark = models.DateTimeField(auto_now_add=True, auto_created=True)
    amount = models.FloatField(verbose_name='')
    franchise = models.FloatField(verbose_name='Франшиза', default=0)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_expenses')
    counterpart = models.ForeignKey(Counterpart, on_delete=models.CASCADE, related_name='counterpart_expenses')
    description = models.TextField()
    expenseType = models.ForeignKey(ExpensesTypes, on_delete=models.CASCADE)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='expense')
    created_by = CreatingUserField(related_name="created_expenses")

    def __str__(self):
        return f'FROM:{self.account.name} TO:{self.counterpart.name} ' \
               f'{self.amount}{self.account.get_currency()} - {self.expenseType.name}'

    class Meta:
        verbose_name = 'Затрата'
        verbose_name_plural = 'Затраты'
