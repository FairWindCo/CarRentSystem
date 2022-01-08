import math

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from balance.models import CashBox, Account
from balance.services import Balance
from django_helpers.admin import CustomModelPage
from carmanagment.models import Car
from carmanagment.serivices.car_rent_service import CarRentService


class MoveCashPage(CustomModelPage):
    title = 'Переместить деньги в другую кассу'  # set page title
    # Define some fields.
    amount = models.FloatField(verbose_name='Сумма')
    from_cash_box = models.ForeignKey(CashBox, on_delete=models.CASCADE, verbose_name='Касса',
                                      related_name='moved_cash_box')
    to_cash_box = models.ForeignKey(CashBox, on_delete=models.CASCADE, verbose_name='Касса',
                                    related_name='recipient_cash_box')

    def clean(self):
        if self.from_cash_box.current_balance() <= self.amount:
            raise ValidationError(_('В кассе недостаточно денег'))

        super().clean()

    def save(self):
        if Balance.form_transaction(Balance.DEPOSIT, [
            (self.from_cash_box, self.to_cash_box, math.trunc(self.amount * 100), 'Перемешение средств'),
        ], 'Перемешение денег между кассами'):
            self.bound_admin.message_success(self.bound_request, _('Поездка добавлена'))


class InsertCashPage(CustomModelPage):
    title = 'Внести деньги в кассу'  # set page title
    # Define some fields.
    amount = models.FloatField(verbose_name='Сумма')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Баланс',
                                related_name='moved_account_rel')
    cash_box = models.ForeignKey(CashBox, on_delete=models.CASCADE, verbose_name='Касса',
                                 related_name='recipient_cash_box_rel')

    def clean(self):
        super().clean()

    def save(self):
        if Balance.form_transaction(Balance.DEPOSIT, [
            (None, self.cash_box, math.trunc(self.amount * 100), 'Пополнение кассы'),
            (None, self.account, math.trunc(self.amount * 100), 'Внесение денег в кассу'),
        ], 'Перемешение денег между кассами'):
            self.bound_admin.message_success(self.bound_request, _('Поездка добавлена'))


class CarRentPage(CustomModelPage):
    title = 'Вывод прибыли по машине'  # set page title
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Модель')
    amount = models.FloatField(verbose_name='Сумма', validators=[
        MinValueValidator(0.01)
    ])

    def clean(self):
        if not hasattr(self, 'car') or self.car is None:
            raise ValidationError(_('Машина обязательна'))
        super().clean()

    def save(self):
        if not self.bound_request.user and not hasattr(self.bound_request.user, 'userprofile'):
            raise ValidationError(_('Пользователь не могут списывать прибыли'))
        firm_account = self.bound_request.user.userprofile.account
        result, message = CarRentService.move_rent_many(self.car, self.amount, firm_account)
        if result:
            self.bound_admin.message_success(self.bound_request, _('прибыль списана'))
        else:
            self.bound_admin.message_error(self.bound_request, message)