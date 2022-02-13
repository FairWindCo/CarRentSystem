from audit_log.models import CreatingUserField
from django.db import models, transaction, IntegrityError
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.utils.timezone import now

from balance.models import CashBox, Transaction, Account
from car_management.models import Counterpart, Car, Driver, RentTerms, get_fuel_price_for_type
from car_management.models.rent_price import StatisticsType
from car_rent.calculators import TripCalculator
from car_rent.calculators.transactions import make_transactions_for_trip, TransactionType
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
    def make_paid_transaction(car: Car, driver: Driver, payer: TaxiOperator, calc, many_cash_box, start, comment,
                              transaction_saving=TransactionType.SIMPLE_TRANSACTION):
        return make_transactions_for_trip(car, driver, payer, calc, many_cash_box, start, comment, transaction_saving)

    @staticmethod
    def auto_create_trip(start: datetime, payer: TaxiOperator,
                         uid: str,
                         millage: float,
                         total_trip_many_amount: float,
                         fuel_prices,
                         cash_many: float = 0,
                         ):
        car_in_taxi = CarSchedule.find_schedule_info(uid, start, payer)
        if car_in_taxi:
            stat_type = car_in_taxi.statistics_type
            if stat_type == StatisticsType.DONT_WORK:
                return None
            if stat_type == StatisticsType.TRIP_PAID_DAY:
                paid_type = car_in_taxi.paid_type
            else:
                paid_type = TransactionType.NO_TRANSACTION

            driver = car_in_taxi.driver
            terms = car_in_taxi.term
            car = car_in_taxi.car
            gas_price = get_fuel_price_for_type(car.model.type_class, fuel_prices)
            in_taxi = car_in_taxi.work_in_taxi
            return TaxiTrip.manual_create_taxi_trip(terms, car, driver, start, payer,
                                                    millage,
                                                    total_trip_many_amount, gas_price,
                                                    cash_many, '', payer.cash_box, paid_type, in_taxi)
        else:
            return None

    @staticmethod
    def manual_create_taxi_trip(terms: RentTerms, car: Car, driver: Driver, start: datetime, payer: TaxiOperator,
                                millage: float,
                                total_trip_many_amount: float, gas_price: float, cash_many: float = 0,
                                comment: str = '',
                                many_cash_box: CashBox = None,
                                transaction_type: TransactionType = TransactionType.NO_TRANSACTION,
                                work_in_taxi: bool = True):
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
                calc = TripCalculator.get_calculator(millage, total_trip_many_amount, cash_many,
                                                     gas_price,
                                                     car,
                                                     payer,
                                                     terms
                                                     )

                taxitrip.payer_amount = calc.taxi_aggregator_rent
                taxitrip.driver_amount = calc.driver_salary
                taxitrip.investor_rent = calc.investor_profit

                if work_in_taxi:
                    transaction_record = TaxiTrip.make_paid_transaction(car, driver, payer, calc, many_cash_box,
                                                                        start, comment, transaction_type)
                    taxitrip.is_rent = False
                else:
                    transaction_record = None
                    taxitrip.is_rent = True
                taxitrip.fuel = calc.fuel_cost
                taxitrip.bank_amount = calc.bank_rent
                taxitrip.operating_services = calc.assistance
                taxitrip.transaction = transaction_record
                taxitrip.save()
                # print('OK')

                return True
        except IntegrityError:
            return False


class TripStatistics(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    stat_date = models.DateField(verbose_name='Дата', default=now)
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
    def auto_create_trip(start, payer: TaxiOperator,
                         uid: str,
                         trip_count: int,
                         millage: float,
                         total_trip_many_amount: float,
                         fuel_prices,
                         cash_many: float = 0,
                         ):
        car_in_taxi = CarSchedule.find_schedule_info(uid, start, payer)
        if car_in_taxi:
            stat_type = car_in_taxi.statistics_type
            if stat_type == StatisticsType.DONT_WORK:
                return None
            if stat_type == StatisticsType.TRIP_DAY_PAID:
                paid_type = car_in_taxi.paid_type
            else:
                paid_type = TransactionType.NO_TRANSACTION

            driver = car_in_taxi.driver
            terms = car_in_taxi.term
            car = car_in_taxi.car

            gas_price = get_fuel_price_for_type(car.model.type_class, fuel_prices)
            in_taxi = car_in_taxi.work_in_taxi

            return TripStatistics.manual_create_summary_paid(car, driver, start, payer, terms, millage,
                                                             total_trip_many_amount, gas_price, cash_many,
                                                             trip_count, '', payer.cash_box, in_taxi, paid_type
                                                             )

        return False

    @staticmethod
    def manual_create_summary_paid(car: Car, driver: Driver, start, payer: TaxiOperator, terms: RentTerms,
                                   millage: float,
                                   total_trip_many_amount: float, gas_price: float, cash_many: float = 0, trip_count=0,
                                   comment: str = '',
                                   many_cash_box: CashBox = None, car_in_taxi: bool = True,
                                   transaction_type: TransactionType = TransactionType.NO_TRANSACTION, ):
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
                sum_trip = TripStatistics(car=car, stat_date=start, trip_count=trip_count,
                                          mileage=millage, amount=total_trip_many_amount, cash=cash_many)
                calc = TripCalculator.get_calculator(millage, total_trip_many_amount, cash_many,
                                                     gas_price,
                                                     car,
                                                     payer,
                                                     terms
                                                     )
                if car_in_taxi:
                    TaxiTrip.make_paid_transaction(car, driver, payer, calc, many_cash_box, start, comment,
                                                   transaction_type)
                sum_trip.payer_amount = calc.taxi_aggregator_rent
                sum_trip.driver_amount = calc.driver_salary
                sum_trip.bank_amount = calc.bank_rent
                sum_trip.investor_amount = calc.investor_profit
                sum_trip.fuel = calc.fuel_cost
                sum_trip.operating_services = calc.assistance
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
