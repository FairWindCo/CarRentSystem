from audit_log.models import CreatingUserField
from constance import config
from django.db import models, transaction, IntegrityError
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.utils.timezone import now

from balance.models import CashBox, Transaction, Account
from balance.services import Balance
from car_management.models import Counterpart, Car, Driver
from car_rent.calculators.taxioperatorcalculator import TaxiCalculator
from car_rent.models import TaxiOperator, CarSchedule


class TaxiTrip(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_created=True, verbose_name='Дата начала поездки')

    mileage = models.FloatField(verbose_name='Пробег по трекеру')
    fuel = models.FloatField(verbose_name='Затраты на топливо')
    amount = models.FloatField(verbose_name='Сумма оплаты')
    many_in_cash = models.FloatField(verbose_name='Оплата наличными', default=0)

    payer_amount = models.FloatField(verbose_name='Прибыль сервиса', default=0)
    driver_amount = models.FloatField(verbose_name='Зарплата водителя', default=0)
    bank_amount = models.FloatField(verbose_name='Комиссия банка', default=0)
    operating_services = models.FloatField(verbose_name='Операционные услуги', default=0)
    investor_rent = models.FloatField(verbose_name='Прибыль инвестора', default=0)

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='Водитель, если известно')
    payer = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True,
                              verbose_name='Плательщик/От кого приняли средства', related_name='trips')

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)
    created_by = CreatingUserField(related_name="created_taxi_trips")
    is_rent = models.BooleanField(verbose_name='Упущенная прибыль', default=False)

    @property
    # Сумма денег сервиса (прибыль сервиса + процент банка)
    def total_payer_amount(self):
        return self.payer_amount + self.bank_amount

    @property
    # сумма денег пришедших на машину
    def car_amount(self):
        return self.amount - self.total_payer_amount

    @property
    # Чистая прибыль авто (без операционных затрат и топлива) база для расчета прибыли инвестора
    def clean_car_amount(self):
        return self.car_amount - self.operating_services - self.fuel

    @property
    # прибыль фирмы
    def firm_amount(self):
        return self.clean_car_amount - self.driver_amount - self.investor_rent

    class Meta:
        unique_together = (('car', 'timestamp'),)

    @staticmethod
    def make_paid_transaction(car: Car, driver: Driver, payer: TaxiOperator, calc, many_cash_box, start, comment):
        firm_account = config.FIRM
        if firm_account is None:
            raise ValueError('Need Set Firm account in Config')

        operations = [
            (None, payer, calc.total_trip_many_int, 'Платеж от клиента'),
            (payer, None, calc.payer_interest_int, 'Комисия оператора такси'),
            (payer, car, calc.trip_many_without_bank_int, 'Платеж от оператора'),
            (car, driver, calc.fuel_compensation_int, 'Компенсация топлива'),
            (car, firm_account, calc.operating_costs_int, 'Операционные затраты'),
            (car, driver, calc.driver_money_int, 'Зарплата водителя'),
        ]
        if calc.cash > 0:
            operations.append((driver, None, calc.cash_int, 'Вывод наличных'))
        if calc.bank_rent > 0:
            operations.append((payer, None, calc.bank_rent_int, 'Комисия банка'))
        else:
            operations.append(
                (None, payer, abs(calc.bank_rent_int), 'возврат комисии банка за комисию оператора'))
        if many_cash_box:
            operations.append((None, driver, calc.cash_int, 'Внос денег в кассу'))
            operations.append((None, many_cash_box, calc.cash_int, 'Пополнение кассы'))
        if payer.cash_box:
            payer_balance_cache = calc.credit_cart_many_int
            if calc.bank_rent > 0:
                operations.append(
                    (None, payer.cash_box, payer_balance_cache,
                     f'Пополнение кассы {payer.cash_box.name} за '
                     f'поездку {start} {car.name} {driver.name}'))
            else:
                operations.append(
                    (payer.cash_box, None, payer_balance_cache,
                     f'Снятие с кассы {payer.cash_box.name} за '
                     f'поездку {start} {car.name} {driver.name}'))
        # print(operations)
        # print(fuel_trip, taxitrip.fuel, driver_money)
        transaction_record = Balance.form_transaction(Balance.DEPOSIT, operations, comment if comment
        else f'Поездка {start} {car.name} {driver.name}')
        return transaction_record

    @staticmethod
    def manual_create_trip(start: datetime, payer: TaxiOperator,
                           uid: str,
                           millage: float,
                           total_trip_many_amount: float,
                           gas_price: float,
                           cash_many: float = 0,
                           comment: str = '',
                           many_cash_box: CashBox = None, only_statistics=False, work_in_taxi: bool = True):
        car, driver = CarSchedule.find_schedule_info(uid, start, payer)
        if car and driver:
            TaxiTrip.manual_create_taxi_trip(car, driver, start, payer, millage, total_trip_many_amount, gas_price,
                                             cash_many, comment, many_cash_box, only_statistics, work_in_taxi)
        else:
            raise TypeError('Need Driver and Car account')

    @staticmethod
    def manual_create_taxi_trip(car: Car, driver: Driver, start: datetime, payer: TaxiOperator, millage: float,
                                total_trip_many_amount: float, gas_price: float, cash_many: float = 0,
                                comment: str = '',
                                many_cash_box: CashBox = None, only_statistics=False, work_in_taxi: bool = True):
        if not isinstance(car, Car) or car is None:
            raise TypeError('Need car account')
        if not isinstance(payer, Counterpart) or payer is None:
            raise TypeError('Need Counterpart account')
        try:
            start = start.astimezone(timezone.utc)
            with transaction.atomic():
                tz = timezone.get_current_timezone()
                taxitrip = TaxiTrip(car=car, timestamp=start.replace(tzinfo=tz), driver=driver, payer=payer,
                                    mileage=millage, amount=total_trip_many_amount,
                                    many_in_cash=cash_many, is_rent=not work_in_taxi)
                calc = TaxiCalculator.get_calculator(millage, total_trip_many_amount, cash_many,
                                                     gas_price, car,
                                                     payer,
                                                     driver
                                                     )

                taxitrip.payer_amount = calc.payer_interest_f
                taxitrip.driver_amount = calc.driver_money_f
                taxitrip.investor_rent = calc.investor_profit_f
                if not only_statistics:
                    if work_in_taxi:
                        transaction_record = TaxiTrip.make_paid_transaction(car, driver, payer, calc, many_cash_box,
                                                                            start, comment)
                    else:
                        transaction_record = None
                        taxitrip.is_rent = True
                else:
                    transaction_record = None
                    taxitrip.is_rent = False
                taxitrip.fuel = calc.fuel_price_f
                taxitrip.bank_amount = calc.bank_rent_f
                taxitrip.operating_services = calc.operating_costs_f
                taxitrip.transaction = transaction_record
                taxitrip.save()
                # print('OK')

                return True
        except IntegrityError:
            return False


class TripStatistics(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    stat_date = models.DateField(verbose_name='Дата', default=now())
    # 5 полей про поезду
    trip_count = models.PositiveIntegerField(verbose_name='Кол-во поездок', default=0)
    mileage = models.FloatField(verbose_name='Пробег за поездки', default=0)
    cash = models.FloatField(verbose_name='Сумма наличнных', default=0)
    amount = models.FloatField(verbose_name='Сумма оплаты', default=0)
    fuel = models.FloatField(verbose_name='Затраты на топливо', default=0)
    # 5 полей (основы для расчетов)
    payer_amount = models.FloatField(verbose_name='Прибыль сервиса', default=0)
    bank_amount = models.FloatField(verbose_name='Банк процент', default=0)
    driver_amount = models.FloatField(verbose_name='Зарплата водителя', default=0)
    operating_services = models.FloatField(verbose_name='Операционные затраты', default=0)
    investor_amount = models.FloatField(verbose_name='Прибыль инвестора', default=0)
    # если выставлен флаг, то машина была в аренде и это все теоретические деньги
    car_in_rent = models.BooleanField(verbose_name='Машина в аренде', default=False)

    @staticmethod
    def manual_create_summary_paid(car: Car, driver: Driver, start, payer: TaxiOperator, millage: float,
                                   total_trip_many_amount: float, gas_price: float, cash_many: float = 0, trip_count=0,
                                   comment: str = '',
                                   many_cash_box: CashBox = None, only_statistics=False):
        if not isinstance(car, Car) or car is None:
            raise TypeError('Need car account')
        if not isinstance(payer, Counterpart) or payer is None:
            raise TypeError('Need Counterpart account')
        try:
            if isinstance(start, datetime):
                start = start
            else:
                start = datetime.combine(start, datetime.min)
            with transaction.atomic():
                car_in_rent = CarSchedule.check_date_in_interval(car, start)
                # print(car.name, car_in_rent, type(start))
                if not car_in_rent:
                    driver_schedule = DriversSchedule.get_driver(car, start)
                    driver = driver_schedule if driver_schedule is not None else driver
                    if not isinstance(driver, Driver) or driver is None:
                        raise TypeError('Need Driver account')

                sum_trip = TripStatistics(car=car, stat_date=start, trip_count=trip_count,
                                          mileage=millage, amount=total_trip_many_amount, cash=cash_many)
                calc = TaxiCalculator.get_calculator(millage, total_trip_many_amount, cash_many,
                                                     gas_price, car,
                                                     payer,
                                                     driver
                                                     )
                if not only_statistics and not car_in_rent:
                    TaxiTrip.make_paid_transaction(car, driver, payer, calc, many_cash_box, start, comment)
                sum_trip.payer_amount = calc.payer_interest_f
                sum_trip.driver_amount = calc.driver_money_f
                sum_trip.bank_amount = calc.bank_rent_f
                sum_trip.investor_amount = calc.investor_profit_f
                sum_trip.fuel = calc.fuel_price_f
                sum_trip.operating_services = calc.operating_costs_f
                sum_trip.save()
                return True
        except IntegrityError:
            return False

    @property
    # Сумма денег сервиса (прибыль сервиса + процент банка)
    def total_payer_amount(self):
        return self.payer_amount + self.bank_amount

    @property
    # сумма денег пришедших на машину
    def car_amount(self):
        return self.amount - self.total_payer_amount

    @property
    # Чистая прибыль авто (без операционных затрат и топлива) база для расчета прибыли инвестора
    def clean_car_amount(self):
        return self.car_amount - self.operating_services - self.fuel

    @property
    # прибыль фирмы
    def firm_amount(self):
        return self.clean_car_amount - self.driver_amount - self.investor_amount

    class Meta:
        verbose_name = 'Суточные данные по поездкам в такси'
        unique_together = (('car', 'stat_date', 'car_in_rent'),)
        index_together = (('car', 'stat_date'),)
