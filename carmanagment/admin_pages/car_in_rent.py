import math

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from balance.models import CashBox
from balance.services import Balance
from .custom_admin import CustomModelPage
from carmanagment.models import Car, Driver, CarSchedule


class CarInRentPage(CustomModelPage):
    title = 'Сдача машины в аренду'  # set page title
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Модель')
    start_time = models.DateTimeField(verbose_name='Дата и время начала аренды')
    end_time = models.DateTimeField(verbose_name='Дата и время завершения аренды')
    amount = models.FloatField(verbose_name='Сумма', validators=[
        MinValueValidator(0.01)
    ])
    deposit = models.FloatField(verbose_name='Залог', validators=[
        MinValueValidator(0.01)
    ])
    cash_box = models.ForeignKey(CashBox, on_delete=models.CASCADE, verbose_name='Касса',
                                 related_name='rent_amount_cash_box')
    deposit_cash_box = models.ForeignKey(CashBox, on_delete=models.CASCADE, verbose_name='Касса для залога',
                                         related_name='rent_deposit_cash_box')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name='Касса для залога',
                               related_name='rent_driver_link', null=True, default=None, blank=True)

    def clean(self):
        if not hasattr(self, 'car') or self.car is None:
            raise ValidationError(_('Машина обязательна'))
        if not hasattr(self, 'cash_box') or self.cash_box is None:
            raise ValidationError(_('Касса обязательна'))
        super().clean()

    def save(self):
        amount = math.trunc(self.amount * 100)
        deposit = math.trunc(self.deposit * 100)
        cash_box_deposit = self.deposit_cash_box if self.deposit_cash_box is not None else self.cash_box
        with transaction.atomic():
            car_scheduler = CarSchedule(car=self.car, start_time=self.start_time, end_time=self.end_time,
                                        rent_amount=amount, deposit=deposit)
            car_scheduler.save()
            if Balance.form_transaction(Balance.DEPOSIT, [
                (None, self.cash_box, amount, f'Деньги за аренду {self.car.name}'),
                (None, cash_box_deposit, deposit, f'Залог за аренду {self.car.name}'),
                (self.driver, self.car, amount, f'Деньги за аренду {self.car.name}'),
            ], 'Аренда автомобиля'):
                self.bound_admin.message_success(self.bound_request, _('Аренда запланирована'))