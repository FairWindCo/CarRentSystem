import math

from audit_log.models import CreatingUserField
from constance import config
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction, IntegrityError
# Create your models here.
from django.utils import timezone
from django.utils.datetime_safe import datetime

import CarRentSystem
from balance.models import Account, Transaction
from balance.services import Balance


class CarBrand(models.Model):
    name = models.CharField(max_length=120, verbose_name='Бренд')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'


class CarModel(models.Model):
    class FuelType(models.IntegerChoices):
        A92 = (1, 'Бензин А95')
        A95 = (2, 'Бензин А95')
        DISEL = (3, 'Дизельное топливо')
        GAS = (4, 'Сжиженный газ')

    name = models.CharField(max_length=120, verbose_name='Модель')
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE)
    type_class = models.PositiveSmallIntegerField(choices=FuelType.choices,
                                                  verbose_name='Тип топлива',
                                                  default=FuelType.GAS)

    def __str__(self):
        return f'{self.brand.name} {self.name}'

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'


def get_fuel_price_for_type(fuel_type, fuel_price):
    if fuel_type == CarModel.FuelType.A92:
        return fuel_price['a95']
    elif fuel_type == CarModel.FuelType.A95:
        return fuel_price['a92']
    elif fuel_type == CarModel.FuelType.DISEL:
        return fuel_price['disel']
    elif fuel_type == CarModel.FuelType.GAS:
        return fuel_price['gas']
    else:
        return 1


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


class TaxiOperator(Counterpart):
    cash_profit = models.FloatField(default=0.15, verbose_name='Коифициент прибили с поезди оператора (нал)')
    profit = models.FloatField(default=0.17, verbose_name='Коифициент прибили с поезди оператора (без нал)')

    class Meta:
        verbose_name = 'Оператор такси'
        verbose_name_plural = 'Оператор такси'


class CarsInOperator(models.Model):
    car = models.ForeignKey("Car", on_delete=models.CASCADE, related_name='cars_in_taxi', verbose_name='Машина')
    driver = models.ForeignKey("Driver", on_delete=models.CASCADE, related_name='driver_in_taxi', verbose_name='Машина')
    operator = models.ForeignKey(TaxiOperator, on_delete=models.CASCADE, related_name='taxi_park',
                                 verbose_name='Таксопарк')
    car_uid = models.CharField(max_length=255, blank=True, null=True, verbose_name='Идентификатор машины')

    def __str__(self):
        return f'{self.operator.name} {self.car.name} {self.driver.name}'

    class Meta:
        verbose_name = 'Машины в таксопарках'
        verbose_name_plural = 'Машины в таксопарках'


class InvestmentCarBalance(Account):
    create_date = models.DateField(auto_created=True)

    class Meta:
        verbose_name = 'Инвестор'
        verbose_name_plural = 'Инвесторы'


class Car(Account):
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    car_investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='cars')
    investment = models.OneToOneField(InvestmentCarBalance, on_delete=models.CASCADE, related_name='car')
    year = models.PositiveSmallIntegerField(verbose_name='Год выпуска', validators=[
        MaxValueValidator(2100),
        MinValueValidator(1900)
    ])
    mileage_at_start = models.PositiveIntegerField(verbose_name='Пробег при поступлении', validators=[
        MinValueValidator(0)
    ])
    date_start = models.DateField(auto_now_add=True, auto_created=True)
    control_mileage = models.PositiveIntegerField(verbose_name='Контрольное значени пробега')
    last_TO_date = models.DateField(null=True, blank=True)
    wialon_id = models.CharField(max_length=50, verbose_name='ID в системе WIALON', null=True, blank=True)
    fuel_consumption = models.FloatField(verbose_name='Расход топлива', default=14)
    additional_miilage = models.PositiveIntegerField(verbose_name='Дополнительный километраж на поездку', default=0)

    def __str__(self):
        return f'{self.model.brand.name} {self.model.name} {self.name}'

    class Meta:
        verbose_name = 'Авто'
        verbose_name_plural = 'Авто'


class CarMileage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='mileage')
    mileage_at_start = models.PositiveIntegerField(verbose_name='')


class WialonTrip(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start = models.DateTimeField(auto_now_add=True, auto_created=True, verbose_name='Дата начала поездки')
    end = models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения поездки')
    mileage = models.PositiveIntegerField(verbose_name='Пробег по трекеру')
    fuel = models.PositiveIntegerField(verbose_name='Раход по трекеру')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='Водитель, если известно')


class TaxiTrip(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_created=True, verbose_name='Дата начала поездки')
    mileage = models.FloatField(verbose_name='Пробег по трекеру')
    fuel = models.FloatField(verbose_name='Затраты на топливо')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='Водитель, если известно')
    amount = models.FloatField(verbose_name='Сумма оплаты')
    car_amount = models.FloatField(verbose_name='Сумма прибыли по машине')
    payer_amount = models.FloatField(verbose_name='Прибыль сервиса', default=0)
    driver_amount = models.FloatField(verbose_name='Зарплата водителя', default=0)
    payer = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True,
                              verbose_name='Плательщик/От кого приняли средства', related_name='trips')
    cash = models.BooleanField(verbose_name='Оплата наличными')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    created_by = CreatingUserField(related_name="created_taxi_trips")

    class Meta:
        unique_together = (('car', 'timestamp'),)

    @staticmethod
    def manual_create_taxi_trip(car: Car, driver: Driver, start: datetime, payer: TaxiOperator, millage: float,
                                amount: float, gas_price: int, cash: bool = False, comment: str = ''):
        if not isinstance(car, Car) or car is None:
            raise TypeError('Need car account')
        if not isinstance(driver, Driver) or driver is None:
            raise TypeError('Need Driver account')
        if not isinstance(payer, Counterpart) or payer is None:
            raise TypeError('Need Counterpart account')
        try:
            with transaction.atomic():
                print(start)
                tz = timezone.get_current_timezone()
                taxitrip = TaxiTrip(car=car, timestamp=start.replace(tzinfo=tz), driver=driver, payer=payer,
                                    mileage=millage, amount=amount,
                                    cash=cash)
                # this is millage for calculate fuel price
                fuel_trip = (millage + car.additional_miilage) / 100 * car.fuel_consumption
                fuel_price = round(fuel_trip * gas_price, 2)

                # this is money without taxi service profit
                real_pay = round(amount * (1 - (payer.cash_profit if cash else payer.profit)), 2)

                # this is money without fuel cost
                real_amount = round(real_pay - fuel_price, 2)

                # this is operating costs
                firm_account = config.FIRM
                if firm_account is None:
                    raise ValueError('Need Set Firm account in Config')
                operating_costs = round(real_pay * (car.car_investor.operating_costs_percent / 100), 2)

                # taxi service profit
                taxitrip.payer_amount = round(amount - real_pay, 2)
                # driver profit
                driver_money = round((real_amount - operating_costs) * (driver.profit / 100), 2)
                taxitrip.driver_amount = driver_money
                operations = [
                    (payer, car, math.trunc(real_pay * 100), 'Платеж от оператора'),
                    (car, driver, math.trunc(fuel_price * 100), 'Компенсация топлива'),
                    (car, firm_account, math.trunc(operating_costs * 100), 'Операционные затраты'),
                    (car, driver, math.trunc(driver_money * 100), 'Зарплата водителя'),
                ]
                if cash:
                    operations.append((driver, None, math.trunc(amount * 100), 'Вывод наличных'))
                # print(operations)
                # print(fuel_trip, taxitrip.fuel, driver_money)
                transaction_record = Balance.form_transaction(Balance.DEPOSIT, operations, comment if comment
                else f'Поездка {start} {car.name} {driver.name}')

                taxitrip.fuel = fuel_price
                taxitrip.car_amount = real_pay - fuel_price - driver_money - operating_costs
                taxitrip.transaction = transaction_record
                taxitrip.save()
                print('OK')
                return True
        except IntegrityError:
            return False



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
    amount = models.FloatField()
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


class TripStatistics(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    stat_date = models.DateField(auto_created=True, verbose_name='Дата')
    trip_count = models.PositiveIntegerField(verbose_name='Кол-во поездок', default=0)
    mileage = models.FloatField(verbose_name='Пробег за поездки', default=0)
    fuel = models.FloatField(verbose_name='Затраты на топливо', default=0)
    amount = models.FloatField(verbose_name='Сумма оплаты', default=0)
    car_amount = models.FloatField(verbose_name='Сумма прибыли по машине', default=0)
    payer_amount = models.FloatField(verbose_name='Прибыль сервиса', default=0)
    driver_amount = models.FloatField(verbose_name='Зарплата водителя', default=0)
    expanse_amount = models.FloatField(verbose_name='Затраты по машине', default=0)
    rent_amount = models.FloatField(verbose_name='Прибыль от аренды', default=0)
    lost_amount = models.FloatField(verbose_name='Не полученная прибыль', default=0)
    rent_mileage = models.FloatField(verbose_name='Пробег в аренде', default=0)

    class Meta:
        unique_together = (('car', 'stat_date'),)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account = models.OneToOneField(Account, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'account'),)
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Провили пользователя'

    def __str__(self):
        return f'{self.user.username} {self.account.name}'


class CarInsurance(models.Model):
    car = models.ForeignKey(Car, verbose_name='Машина', on_delete=models.CASCADE)
    start_date = models.DateField(auto_created=True, verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата завершения')
    car_amount = models.FloatField(verbose_name='Страховой взнос', default=0)
    franchise = models.PositiveIntegerField(verbose_name='Франшиза', default=0)
    insurer = models.ForeignKey(Counterpart, verbose_name='Страховщик', on_delete=models.CASCADE)
    is_capital_expense = models.BooleanField(verbose_name='Покрытие капитальных затрат', default=0)
    created_by = CreatingUserField(related_name="created_insurance")

    def clean(self):
        if self.end_date is None or self.start_date is None:
            raise ValidationError('Start Date and end date is required')
        if self.end_date <= self.start_date:
            raise ValidationError('Start date need be less then End date')
        if self.car_amount <= 0:
            raise ValidationError('amount need be great then zero')
        super().clean()

    def validate_unique(self, exclude=None):
        qs = CarInsurance.objects.filter(car=self.car)
        if self.end_date is None or self.start_date is None:
            raise ValidationError('Start Date and end date is required')
        if qs.filter(start_date__gte=self.start_date).exists():
            raise ValidationError('The Car is already insured')
        if qs.filter(end_date__gte=self.end_date).exists():
            raise ValidationError('The Car is already insured')
        if qs.filter(start_date__lt=self.start_date, end_date__gte=self.start_date).exists():
            raise ValidationError('The Car is already insured')
        if qs.filter(start_date__lt=self.start_date, end_date__gte=self.end_date).exists():
            raise ValidationError('The Car is already insured')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        add_monay = self.pk is None
        super().save(force_insert, force_update, using, update_fields)
        if add_monay:
            Balance.form_transaction(Balance.INSURANCE, [
                (self.car.car_investor, self.insurer, math.trunc(self.car_amount * 100),
                 'Капитальные затрата на автомобиль'),
            ], "Страховой взнос")

    class Meta:
        verbose_name = 'Страховка'
        verbose_name_plural = 'Страховки'
        ordering = ['-start_date', '-end_date', 'insurer__name', 'car__name']

    def __str__(self):
        return f'{self.car.name} {self.insurer.name} от {self.start_date} до {self.end_date}'


class DriversSchedule(models.Model):
    car = models.ForeignKey(Car, verbose_name='Машина', on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name='Водитель')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        verbose_name = 'Расписание работы на авто'
        verbose_name_plural = 'Расписания работы на авто'


class CarDayRent(models.Model):
    car = models.ForeignKey(Car, verbose_name='Машина', on_delete=models.CASCADE)
    date = models.DateField(verbose_name='Дата аренды')
    rent_amount = models.FloatField(verbose_name='Ставка оренды', default=0.0)


class CarSchedule(models.Model):
    car = models.ForeignKey(Car, verbose_name='Машина', on_delete=models.CASCADE)
    fix_rent = models.BooleanField(verbose_name='Машина в аренде', default=True)
    rent_price = models.FloatField(verbose_name='Ставка оренды', default=0.0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        verbose_name = 'Расписание работы на авто'
        verbose_name_plural = 'Расписания работы на авто'
