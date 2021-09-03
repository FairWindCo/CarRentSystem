from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from carmanagment.custom_admin import CustomModelPage
from carmanagment.models import *
from carmanagment.services import ExpensesProcessor


class ExpensePage(CustomModelPage):
    title = 'Внести "затрату" по машине'  # set page title
    # Define some fields.
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Авто')
    expense_type = models.ForeignKey(ExpensesTypes, on_delete=models.CASCADE, verbose_name='Тип затраты')
    amount = models.PositiveIntegerField(verbose_name='Сумма')
    counterpart = models.ForeignKey(Counterpart, on_delete=models.CASCADE, verbose_name='Контрагент')
    comment = models.TextField(verbose_name='Коментарий')
    currency_rate = models.FloatField(verbose_name='Курс', null=True, blank=True)

    def clean(self):
        if self.expense_type is None:
            raise ValidationError(_('Тип затьраты обязателен'))
        if self.expense_type.type_class not in [ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE,
                                                ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE,
                                                ]:
            raise ValidationError(_('Не верный класс затраты для машины'))
        if self.expense_type.type_class == ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE and self.currency_rate is None:
            raise ValidationError(_('Для капитальных затрат курс - обязателен'))
        super().clean()

    def save(self):
        if not hasattr(self, 'expense_type'):
            raise ValidationError(_('Тип затраты обязателен'))
        if self.expense_type.type_class == ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE:
            ExpensesProcessor.form_car_capital_expense(
                self.car, self.amount, self.currency_rate, self.expense_type, self.counterpart, self.comment)
        elif self.expense_type.type_class == ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE:
            ExpensesProcessor.form_car_current_expense(self.car, self.amount, self.expense_type,
                                                       self.counterpart, self.comment)
        else:
            raise ValidationError(_('Не верный класс затраты для машины'))


class OtherExpensePage(CustomModelPage):
    title = 'Внести "затрату"'  # set page title
    # Define some fields.
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Аккаунт')
    expense_type = models.ForeignKey(ExpensesTypes, on_delete=models.CASCADE, verbose_name='Тип затраты')
    amount = models.PositiveIntegerField(verbose_name='Сумма')
    counterpart = models.ForeignKey(Counterpart, on_delete=models.CASCADE, verbose_name='Контрагент',
                                    related_name='other_expense')
    comment = models.TextField(verbose_name='Коментарий')

    def clean(self):
        if not hasattr(self, 'expense_type'):
            raise ValidationError(_('Тип затраты обязателен'))
        if not hasattr(self, 'account'):
            raise ValidationError(_('Аккаунт обязателен'))
        if self.expense_type.type_class == ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE or \
                self.expense_type.type_class == ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE or \
                isinstance(self.account, Car) or self.account.car is not None:
            raise ValidationError(_('Затраты для машины - заносятся отдельно'))
        if self.account.currency == Account.AccountCurrency.DOLLAR:
            raise ValidationError(_('Внос капитальных затрат не разрешен'))
        super().clean()

    def save(self):
        if self.expense_type is None:
            raise ValidationError(_('Тип затьраты обязателен'))
        if self.expense_type.type_class == ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE or \
                self.expense_type.type_class == ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE:
            raise ValidationError(_('Затраты для машины - заносятся отдельно'))
        else:
            ExpensesProcessor.form_expense(self.account, self.amount, self.expense_type,
                                           self.counterpart, self.comment)
