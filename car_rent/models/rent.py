from datetime import timedelta
from math import trunc

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, F
from django.utils.datetime_safe import datetime
from django.utils.timezone import now

from car_management.models import Car, Driver, RentTerms, TimeType
from car_management.models.rent_price import TransactionType, StatisticsType
from .taxi_operator import TaxiOperator
from .car_in_operators import CarsInOperator


class CarScheduleBase(models.Model):
    car = models.ForeignKey(Car, verbose_name='Машина', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True, default=None)

    def clean(self):
        if self.start_time is None:
            raise ValidationError('Start Date and end date is required')
        if self.end_time and self.end_time <= self.start_time:
            raise ValidationError('Start date need be less then End date')
        if self.end_time:
            if self.__class__.objects.filter(car=self.car).filter(~Q(pk=self.pk)).filter(
                    Q(start_time__lte=self.start_time, end_time__gte=self.start_time) |
                    Q(start_time__lte=self.end_time, end_time__gte=self.end_time) |
                    Q(start_time__lte=self.start_time, end_time__isnull=True) |
                    Q(start_time__lte=self.end_time, end_time__isnull=True)
            ).exists():
                raise ValidationError('Эта машина уже запланирована')
        else:
            if self.__class__.objects.filter(car=self.car).filter(end_time__isnull=True).exists():
                raise ValidationError('Для этой машины уже есть открытый интервал')
            if self.__class__.objects.filter(car=self.car).filter(
                    Q(start_time__lte=self.start_time, end_time__gte=self.start_time) |
                    Q(start_time__gte=self.start_time, end_time__gte=self.start_time)
            ).exists():
                raise ValidationError('Эта машина уже запланирована')

    @classmethod
    def queryset_for_date(cls, car: Car, date_time: datetime):
        queryset = cls.objects.filter(car=car).filter(
            start_time__lte=date_time, end_time__gte=date_time
        )
        return queryset

    @classmethod
    def check_date_in_interval(cls, car: Car, date_time: datetime) -> bool:
        return cls.queryset_for_date(car, date_time).exists()

    @classmethod
    def object_date_in_interval(cls, car: Car, date_time: datetime):
        try:
            return cls.queryset_for_date(car, date_time).first()
        except cls.DoesNotExist:
            return None

    def interval(self):
        return self.end_time - self.start_time

    @classmethod
    def get_object_from_date(cls, car: Car, date_time: datetime):
        try:
            result = cls.objects.filter(car=car).filter(
                Q(start_time__gte=date_time, end_time__lte=date_time)
            ).annotate(ordering=F('start_time') - F('end_time')).order_by(
                "-ordering").first()
        except cls.DoesNotExist:
            result = None
        return result

    class Meta:
        abstract = True
        verbose_name = 'Расписание для авто'
        verbose_name_plural = 'Расписания для авто'


class CarSchedule(CarScheduleBase):
    end_rent = models.DateTimeField(verbose_name='Аренда завершена', default=None, null=True, blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name='Арендатор', blank=True, null=True)
    term = models.ForeignKey(RentTerms, on_delete=models.CASCADE, verbose_name='условия аренды',
                             related_name='scheduled_terms')
    taxi_operators = models.ManyToManyField(CarsInOperator, verbose_name='операторы такси')
    deposit = models.FloatField(verbose_name='Требуемый залог', default=0.0)
    paid_deposit = models.FloatField(verbose_name='Оплаченный залог', default=0.0)
    amount = models.FloatField(verbose_name='Оплаченная сумма за аренду', default=0.0)
    work_in_taxi = models.BooleanField(verbose_name='Работает в нашем такси', default=False)
    min_time = models.PositiveIntegerField(verbose_name='Минимальный срок аренды', default=0)
    can_break_rent = models.BooleanField(verbose_name='Разрешен досочный возврат', default=True)
    statistics_type = models.PositiveIntegerField(choices=StatisticsType.choices, default=StatisticsType.TRIP_DAY_PAID,
                                                  verbose_name='Тип собираемой статистики')
    paid_type = models.PositiveIntegerField(choices=TransactionType.choices, default=TransactionType.NO_TRANSACTION,
                                            verbose_name='Тип проводимых платежей')

    auto_renew = models.BooleanField(verbose_name='Автоматически обновлять план аренды', default=False)


    @classmethod
    def queryset_for_date(cls, car: Car, date_time: datetime):
        queryset = cls.queryset_date_filter(date_time).filter(car=car)
        return queryset

    @classmethod
    def queryset_date_filter(cls, date_time: datetime):
        queryset = cls.objects.filter(
            Q(start_time__lte=date_time, end_time__gte=date_time, end_rent__isnull=True) |
            Q(start_time__lte=date_time, end_rent__gte=date_time, end_rent__isnull=False)
        ).order_by('-start_time', '-end_time')
        return queryset

    def calculate_time_interval(self, delta: timedelta, min_time):
        time = delta if delta > min_time else min_time
        return self.time_interval(time)

    def time_interval(self, delta: timedelta):
        if self.term.type_class == TimeType.DAYS:
            days = delta.days
            if delta.seconds > 0:
                days += 1
            return days
        else:
            hours = 24 * delta.days + int(delta.seconds / 3600)
            minutes = delta.seconds % 3600
            if minutes > 0:
                hours += 1
            return hours

    def minimal(self):
        if self.term.type_class == TimeType.DAYS:
            return timedelta(days=self.min_time)
        else:
            return timedelta(seconds=self.min_time * 3600)

    @property
    def plan_rent_interval(self):
        return self.calculate_time_interval(self.start_time - self.end_time, self.minimal())

    @property
    def rent_price(self):
        if self.amount > 0:
            return round(self.amount / self.plan_rent_interval, 2)
        else:
            return round(self.amount, 2)

    def rent_interval(self):
        return self.calculate_time_interval(self.end_time - self.start_time, self.minimal())

    def current_return_many(self, end_date: datetime = now()):
        if not self.can_break_rent:
            return 0
        if not self.work_in_taxi:
            return 0

        if self.end_rent is None:
            if self.amount <= 0:
                return 0
            else:
                minimal = self.minimal()
                plan = self.calculate_time_interval(self.end_time - self.start_time, minimal)
                fact = self.calculate_time_interval(end_date - self.start_time, minimal)
                interval = plan - fact
                # print(interval)
                return round(self.rent_price * interval, 2)
        else:
            return 0

    def current_return(self, end_date: datetime = now()):
        if self.end_rent is None:
            return_price = self.current_return_many(end_date)
            if return_price < 0:
                delta_deposit = self.paid_deposit + return_price
                return 0, delta_deposit
            return return_price, round(self.paid_deposit, 2)
        else:
            return 0, 0

    @classmethod
    def find_schedule_info(cls, uid: str, date_time: datetime, operator: TaxiOperator):
        try:
            taxi_in_operator = CarsInOperator.objects.filter(operator=operator, car_uid=uid).first()
            # print(taxi_in_operator, uid)
            if taxi_in_operator:
                data = cls.queryset_date_filter(date_time).filter(taxi_operators=taxi_in_operator).first()
                # print(data)
                return data
            else:
                return None
        except cls.DoesNotExist:
            return None

    @property
    def return_many(self):
        return trunc(self.current_return_many() * 100)

    @property
    def return_deposit(self):
        return trunc(self.paid_deposit * 100)

    def __str__(self):
        start_date_formatted = self.start_time.strftime('%d.%m.%y %H:%M:%S') if self.start_time else '--'
        end_date_formatted = self.end_time.strftime('%d.%m.%y %H:%M:%S') if self.end_time else '--'
        return f'{self.car.name} {self.amount} от {start_date_formatted} до {end_date_formatted} ' \
               f'{self.current_return_many()} {self.paid_deposit}'

    class Meta:
        verbose_name = 'Аренда авто'
        verbose_name_plural = 'Расписание аренды авто'
        app_label = 'car_rent'
