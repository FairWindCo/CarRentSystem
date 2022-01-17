import math
from datetime import timedelta
from math import trunc

from constance import config

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, F
from django.utils.timezone import now

from carmanagment.models import Car, Driver, RentPrice
from django.utils.datetime_safe import datetime


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
            if self.__class__.objects.filter(car=self.car).filter(
                    Q(start_time__lte=self.start_time, end_time__gte=self.start_time) |
                    Q(start_time__lte=self.end_time, end_time__gte=self.end_time) |
                    Q(start_time__lte=self.start_time, end_time__isnull=True) |
                    Q(start_time__lte=self.end_time, end_time__isnull=True)
            ).exists():
                raise ValidationError('Эта машина уже запланирована')
        else:
            if self.__class__.objects.filter(car=self.car).filter(end_time__isnull=True).exists():
                raise ValidationError('Для этой машины уже есть октрытый интервал')
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


class DriversSchedule(CarScheduleBase):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name='Водитель')

    @classmethod
    def get_driver(cls, car, current_date):
        cars = cls.objects.annotate(ordering=F('end_time') - F('start_time')).filter(car=car)
        try:
            driver = cars.filter(start_time__gte=current_date, end_time__lte=current_date).order_by('ordering',
                                                                                                    'id').first()
            if driver:
                return driver.driver
            else:
                driver = cars.filter(start_time__gte=current_date, end_time__isnull=True).order_by('id').first()
                if driver:
                    return driver.driver
        except cls.DoesNotExist:
            try:
                driver = cars.filter(start_time__gte=current_date, end_time__isnull=True).order_by('id').first().driver
            except cls.DoesNotExist:
                driver = None
        return driver

    def __str__(self):
        return f'{self.car.name} {self.driver.name} от {self.start_time} до {self.end_time}'

    class Meta:
        verbose_name = 'Расписание работы на авто'
        verbose_name_plural = 'Расписания работы на авто'


class CarSchedule(CarScheduleBase):
    end_rent = models.DateTimeField(verbose_name='Аренда завершена', default=None, null=True, blank=True)
    deposit = models.FloatField(verbose_name='Залог', default=0.0)
    paid_deposit = models.FloatField(verbose_name='Оплаченый залог', default=0.0)
    amount = models.FloatField(verbose_name='Оплаченый залог', default=0.0)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name='Арендатор', blank=True, null=True)
    price = models.ForeignKey(RentPrice, on_delete=models.CASCADE, verbose_name='тариф', related_name='scheduled_price')

    @classmethod
    def queryset_for_date(cls, car: Car, date_time: datetime):
        queryset = cls.objects.filter(car=car).filter(
            Q(start_time__lte=date_time, end_time__gte=date_time, end_rent__isnull=True) |
            Q(start_time__lte=date_time, end_rent__gte=date_time, end_rent__isnull=False)
        )
        return queryset

    @property
    def plan_rent_interval(self):
        return self.price.calculate_time_interval(self.start_time - self.end_time, self.price.minimal())

    @property
    def rent_price(self):
        if self.amount > 0:
            return round(self.amount / self.plan_rent_interval, 2)
        else:
            return round(self.price.price, 2)

    def rent_interval(self):
        return self.price.calculate_time_interval(self.end_time - self.start_time, self.price.minimal())

    def current_return_many(self, end_date: datetime = now()):
        if self.end_rent is None:
            if self.amount <= 0:
                return round(self.price.get_return_price(self.start_time, self.end_time, end_date), 2)
            else:
                minimal = self.price.minimal()
                plan = self.price.calculate_time_interval(self.end_time - self.start_time, minimal)
                fact = self.price.calculate_time_interval(end_date - self.start_time, minimal)
                interval = plan - fact
                print(interval)
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

    @property
    def return_many(self):
        return trunc(self.current_return_many() * 100)

    @property
    def return_deposit(self):
        return trunc(self.paid_deposit * 100)

    def __str__(self):
        start_date_formtted = self.start_time.strftime('%d.%m.%y %H:%M:%S') if self.start_time else '--'
        end_date_formtted = self.end_time.strftime('%d.%m.%y %H:%M:%S') if self.end_time else '--'
        return f'{self.car.name} {self.price.price} от {start_date_formtted} до {end_date_formtted} ' \
               f'{self.current_return_many()} {self.paid_deposit}'

    class Meta:
        verbose_name = 'Аренда авто'
        verbose_name_plural = 'Расписание аренды авто'
        app_label = 'carrent'
