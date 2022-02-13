import math
from datetime import timedelta

from constance import config
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Q
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from balance.models import CashBox
from balance.services import Balance
from car_rent.models import CarSchedule
from django_helpers.admin import CustomModelPage
from django_helpers.admin.artificial_admin_models import CustomPageModelAdmin
from django_helpers.admin import ReadonlyAdmin
from car_management.models import Car, Driver



class CarRentPageAdmin(ReadonlyAdmin):
    ordering = ['-end_time', '-start_time', 'car__name']
    search_fields = ['car__name']

    def get_search_results(self, request, queryset, search_term):
        print("In get search results", request)

        if 'model_name' in request.GET:
            if request.GET['model_name'] == 'returncarrentpage':
                queryset = queryset.filter(end_rent__isnull=True)
        results = super().get_search_results(request, queryset, search_term)
        return results


class CarInRentPage(CustomModelPage):
    app_label = 'car_rent'
    title = 'Сдача машины в аренду'  # set page title
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Модель')
    start_time = models.DateTimeField(verbose_name='Дата и время начала аренды', default=now)
    end_time = models.DateTimeField(verbose_name='Дата и время завершения аренды',
                                    default=(now() + timedelta(days=config.MIN_RENT)))
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
        # if self.car.rent_price_plan:
        #
        super().clean()

    def save(self):
        amount = math.trunc(self.amount * 100)
        deposit = math.trunc(self.deposit * 100)
        cash_box_deposit = self.deposit_cash_box if self.deposit_cash_box is not None else self.cash_box
        with transaction.atomic():
            car_scheduler = CarSchedule(car=self.car, start_time=self.start_time, end_time=self.end_time,
                                        rent_amount=round(self.amount, 2),
                                        deposit=round(self.deposit, 2))
            car_scheduler.save()
            if Balance.form_transaction(Balance.DEPOSIT, [
                (None, self.cash_box, amount, f'Деньги за аренду {self.car.name}'),
                (None, cash_box_deposit, deposit, f'Залог за аренду {self.car.name}'),
                (None, self.car, amount, f'Деньги за аренду {self.car.name}'),
            ], 'Аренда автомобиля'):
                self.bound_admin.message_success(self.bound_request, _('Аренда запланирована'))


class ReturnCarRentPage(CustomModelPage):
    app_label = 'car_rent'
    title = 'Срочный возврат машины из аренды'  # set page title
    car_in_rent = models.ForeignKey(CarSchedule, on_delete=models.CASCADE, verbose_name='Аренда')
    cash_box = models.ForeignKey(CashBox, on_delete=models.CASCADE, verbose_name='Взять средства из касса',
                                 related_name='return_amount_cash_box')
    deposit_cash_box = models.ForeignKey(CashBox, on_delete=models.CASCADE,
                                         verbose_name='Вернуть деньги из кассы для залога',
                                         related_name='return_deposit_cash_box')

    def clean(self):
        if not hasattr(self, 'car_rent') or self.car_rent is None:
            raise ValidationError(_('Необходимо выбрать возврат'))
        if not hasattr(self, 'cash_box') or self.cash_box is None:
            raise ValidationError(_('Необходимо выбрать кассу для возврата'))
        if not hasattr(self, 'deposit_cash_box') or self.deposit_cash_box is None:
            raise ValidationError(_('Необходимо выбрать кассу для возврата депозита'))
        return_many = self.car_in_rent.return_many
        cach_balance = self.cash_box.get_current_balance()
        if return_many <= 0 or not self.car_in_rent.my_break_rent:
            raise ValidationError(_('Эту аренду нельзя прервать'))
        if cach_balance < return_many:
            raise ValidationError(_('В выбранной кассе не достаточно средств'))
        if self.deposit_cash_box.get_current_balance() < self.car_in_rent.deposit:
            raise ValidationError(_('В выбранной кассе не достаточно средств'))
        super().clean()

    def save(self):
        with transaction.atomic():
            self.car_in_rent.end_rent = True
            self.car_in_rent.end_rent = now()
            self.car_in_rent.save()
            return_many = self.car_in_rent.return_many
            if Balance.form_transaction(Balance.WITHDRAWAL, [
                (self.cash_box, None, return_many, f'Возврат денег за не полную аренду  {self.car_in_rent.car.name}'),
                (self.deposit_cash_box, None, self.car_in_rent.deposit,
                 f'Возврат залога за аренду {self.car_in_rent.car.name}'),
                (self.car_in_rent.car, None, return_many, f'Возврат денег за не полную аренду  {self.car_in_rent.car.name}'),
            ], 'Аренда автомобиля'):
                self.bound_admin.message_success(self.bound_request, _('Аренда завершена'))


class ReturnCarRentPageAdmin(CustomPageModelAdmin):
    autocomplete_fields = ('car_in_rent',)


class AddDepositCarRentPageAdmin(CustomPageModelAdmin):
    autocomplete_fields = ('car_in_rent',)


class AddDepositCarRentPage(CustomModelPage):
    app_label = 'car_rent'
    title = 'Добавить депозитные средства'  # set page title
    car_in_rent = models.ForeignKey(CarSchedule, on_delete=models.CASCADE, verbose_name='Аренда')
    amount = models.FloatField(verbose_name='Сумма', validators=[
        MinValueValidator(0.01)
    ])
    cash_box = models.ForeignKey(CashBox, on_delete=models.CASCADE, verbose_name='Внести средства в кассу',
                                 related_name='deposit_amount_cash_box')

    def clean(self):
        if not hasattr(self, 'car_rent') or self.car_in_rent is None:
            raise ValidationError(_('Необходимо выбрать возврат'))
        if not hasattr(self, 'amount') or self.amount > 0:
            raise ValidationError(_('Необходимо указать сумму'))
        if not hasattr(self, 'cash_box') or self.cash_box is None:
            raise ValidationError(_('Необходимо выбрать кассу для депозита'))
        if self.car_in_rent.paid_deposit + self.amount > self.car_in_rent.deposit:
            raise ValidationError(_('Превишен депозит'))

    def save(self):
        with transaction.atomic():
            self.car_in_rent.paid_deposit += self.amount
            self.car_in_rent.save()
            amount = round(self.amount * 100)
            if Balance.form_transaction(Balance.WITHDRAWAL, [
                (None, self.cash_box, amount, f'Доплата депозита {self.car_in_rent.car.name}'),
            ], 'Аренда автомобиля'):
                self.bound_admin.message_success(self.bound_request, _('Доплата депозита'))


class PenaltyDepositCarRentPageAdmin(CustomPageModelAdmin):
    autocomplete_fields = ('car_in_rent',)


class PenaltyDepositCarRentPage(CustomModelPage):
    title = 'Штраф на арендованую машину'  # set page title
    car_in_rent = models.ForeignKey(CarSchedule, on_delete=models.CASCADE, verbose_name='Аренда')
    amount = models.FloatField(verbose_name='Сумма', validators=[
        MinValueValidator(0.01)
    ])
    app_label = 'car_rent'

    def clean(self):
        if not hasattr(self, 'car_rent') or self.car_in_rent is None:
            raise ValidationError(_('Необходимо выбрать возврат'))
        if not hasattr(self, 'amount') or self.amount > 0:
            raise ValidationError(_('Необходимо указать сумму'))

    def save(self):
        with transaction.atomic():
            self.car_in_rent.paid_deposit -= self.amount
            self.car_in_rent.save()
            amount = round(self.amount * 100)
            if Balance.form_transaction(Balance.WITHDRAWAL, [
                (None, self.car_in_rent.car, amount, f'Штраф с депозита {self.car_in_rent.car.name}'),
            ], 'Аренда автомобиля'):
                self.bound_admin.message_success(self.bound_request, _('Доплата депозита'))
