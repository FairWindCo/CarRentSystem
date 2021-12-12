import math

from audit_log.models import CreatingUserField
from constance import config
from django.db import models, transaction, IntegrityError
from django.utils import timezone
from django.utils.datetime_safe import datetime

from balance.models import CashBox, Transaction, Account
from balance.services import Balance
from carmanagment.models import Counterpart, Car, Driver, CarSchedule, DriversSchedule
from carmanagment.models.taxioperatorcalculator import TaxiCalculator


class TaxiOperator(Counterpart):
    cash_profit = models.FloatField(default=0.15, verbose_name='Коифициент прибили с поезди оператора (нал)')
    profit = models.FloatField(default=0.15, verbose_name='Коифициент прибили с поезди оператора (без нал)')
    bank_interest = models.FloatField(default=0.025, verbose_name='Комисия за перевод (без нал)')
    cash_box = models.ForeignKey(CashBox, on_delete=models.CASCADE, null=True, blank=True)

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
    many_in_cash = models.FloatField(verbose_name='Оплата наличными', default=0)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)
    created_by = CreatingUserField(related_name="created_taxi_trips")
    is_rent = models.BooleanField(verbose_name='Упущенная прибыль', default=False)
    bank_amount = models.FloatField(verbose_name='Комисия банка', default=0)
    total_payer_amount = models.FloatField(verbose_name='Деньги сервиса', default=0)
    firm_rent = models.FloatField(verbose_name='Операционные услуги', default=0)

    class Meta:
        unique_together = (('car', 'timestamp'),)

    @staticmethod
    def manual_create_taxi_trip(car: Car, driver: Driver, start: datetime, payer: TaxiOperator, millage: float,
                                total_trip_many_amount: float, gas_price: float, cash_many: float = 0,
                                comment: str = '',
                                many_cash_box: CashBox = None):
        if not isinstance(car, Car) or car is None:
            raise TypeError('Need car account')
        if not isinstance(payer, Counterpart) or payer is None:
            raise TypeError('Need Counterpart account')
        try:
            with transaction.atomic():
                car_in_rent = CarSchedule.check_date_in_interval(car, start)
                if not car_in_rent:
                    driver_schedule = DriversSchedule.get_object_from_date(car, start)
                    driver = driver_schedule if driver_schedule is not None else driver
                    if not isinstance(driver, Driver) or driver is None:
                        raise TypeError('Need Driver account')
                else:
                    driver = None
                    payer = None

                tz = timezone.get_current_timezone()
                taxitrip = TaxiTrip(car=car, timestamp=start.replace(tzinfo=tz), driver=driver, payer=payer,
                                    mileage=millage, amount=total_trip_many_amount,
                                    many_in_cash=cash_many)
                calc = TaxiCalculator(millage, total_trip_many_amount, cash_many,
                                      car.fuel_consumption, gas_price, car.additional_miilage,
                                      payer.cash_profit, payer.profit, payer.bank_interest,
                                      car.car_investor.operating_costs_percent,
                                      driver.profit
                                      )

                firm_account = config.FIRM
                if firm_account is None:
                    raise ValueError('Need Set Firm account in Config')
                taxitrip.payer_amount = calc.payer_interest
                taxitrip.driver_amount = calc.driver_money
                if not car_in_rent:
                    operations = [
                        (None, payer, math.trunc(calc.total_trip_many * 100), 'Платеж от клиента'),
                        (payer, None, math.trunc(calc.payer_interest * 100), 'Комисия оператора такси'),
                        (payer, car, math.trunc(calc.trip_many_without_bank * 100), 'Платеж от оператора'),
                        (car, driver, math.trunc(calc.fuel_price * 100), 'Компенсация топлива'),
                        (car, firm_account, math.trunc(calc.operating_costs * 100), 'Операционные затраты'),
                        (car, driver, math.trunc(calc.driver_money * 100), 'Зарплата водителя'),
                    ]
                    if calc.cash > 0:
                        operations.append((driver, None, math.trunc(calc.cash * 100), 'Вывод наличных'))
                    if calc.bank_rent > 0:
                        operations.append((payer, None, math.trunc(calc.bank_rent * 100), 'Комисия банка'))
                    if many_cash_box:
                        operations.append((None, driver, math.trunc(calc.cash * 100), 'Внос денег в кассу'))
                        operations.append((None, many_cash_box, math.trunc(calc.cash * 100), 'Пополнение кассы'))
                    if payer.cash_box:
                        payer_balance_cache = calc.credit_cart_many
                        if payer_balance_cache > 0:
                            operations.append(
                                (None, payer.cash_box, math.trunc(payer_balance_cache * 100),
                                 f'Пополнение кассы {payer.cash_box.name} за '
                                 f'поездку {start} {car.name} {driver.name}'))
                        else:
                            operations.append(
                                (payer.cash_box, None, math.trunc(payer_balance_cache * 100),
                                 f'Пополнение кассы {payer.cash_box.name} за '
                                 f'поездку {start} {car.name} {driver.name}'))
                    # print(operations)
                    # print(fuel_trip, taxitrip.fuel, driver_money)
                    transaction_record = Balance.form_transaction(Balance.DEPOSIT, operations, comment if comment
                    else f'Поездка {start} {car.name} {driver.name}')
                else:
                    transaction_record = None
                    taxitrip.is_rent = True

                taxitrip.fuel = calc.fuel_price
                taxitrip.car_amount = calc.firm_profit
                taxitrip.bank_amount = calc.bank_rent
                taxitrip.firm_rent = calc.operating_costs
                taxitrip.total_payer_amount = calc.total_payer_amount
                taxitrip.transaction = transaction_record
                taxitrip.save()
                print('OK')
                return True
        except IntegrityError:
            return False


class TripStatistics(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    stat_date = models.DateField(auto_created=True, verbose_name='Дата')
    trip_count = models.PositiveIntegerField(verbose_name='Кол-во поездок', default=0)
    mileage = models.FloatField(verbose_name='Пробег за поездки', default=0)
    fuel = models.FloatField(verbose_name='Затраты на топливо', default=0)
    cash = models.FloatField(verbose_name='Сумма наличнных', default=0)
    amount = models.FloatField(verbose_name='Сумма оплаты', default=0)
    car_amount = models.FloatField(verbose_name='Сумма прибыли по машине', default=0)
    payer_amount = models.FloatField(verbose_name='Прибыль сервиса', default=0)
    driver_amount = models.FloatField(verbose_name='Зарплата водителя', default=0)
    expanse_amount = models.FloatField(verbose_name='Затраты по машине', default=0)
    rent_amount = models.FloatField(verbose_name='Прибыль от аренды', default=0)
    lost_amount = models.FloatField(verbose_name='Не полученная прибыль', default=0)
    rent_mileage = models.FloatField(verbose_name='Пробег в аренде', default=0)
    total_payer_amount = models.FloatField(verbose_name='Деньги для сервиса', default=0)
    total_firm_rent = models.FloatField(verbose_name='Операционные затрты', default=0)
    total_bank_rent = models.FloatField(verbose_name='Банк процент', default=0)

    class Meta:
        unique_together = (('car', 'stat_date'),)
