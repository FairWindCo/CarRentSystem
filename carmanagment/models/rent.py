from datetime import timedelta
from math import trunc

from constance import config

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, F
from django.utils.timezone import now

from carmanagment.models import Car, Driver
from django.utils.datetime_safe import datetime


class CarSchedule(models.Model):
    car = models.ForeignKey(Car, verbose_name='Машина', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def clean(self):
        if self.end_time is None or self.start_time is None:
            raise ValidationError('Start Date and end date is required')
        if self.end_time <= self.start_time:
            raise ValidationError('Start date need be less then End date')
        if self.__class__.objects.filter(car=self.car).filter(
                Q(start_time__lte=self.start_time, end_time__gte=self.start_time) |
                Q(start_time__lte=self.end_time, end_time__gte=self.end_time)
        ).exists():
            raise ValidationError('Эта машина уже запланирована')

    @classmethod
    def check_date_in_interval(cls, car: Car, date_time: datetime) -> bool:
        queryset = cls.objects.filter(car=car).filter(
            start_time__lte=date_time, end_time__gte=date_time
        )
        return queryset.exists()

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


class DriversSchedule(CarSchedule):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name='Водитель')

    def __str__(self):
        return f'{self.car.name} {self.driver.name} от {self.start_time} до {self.end_time}'

    class Meta:
        verbose_name = 'Расписание работы на авто'
        verbose_name_plural = 'Расписания работы на авто'


class CarSchedule(CarSchedule):
    plan_rent = models.BooleanField(verbose_name='Запланированная аренда', default=False)
    end_rent = models.BooleanField(verbose_name='Аренда завершена досрочно', default=False)
    my_break_rent = models.BooleanField(verbose_name='Разрешен досочный возврат', default=True)
    rent_amount = models.FloatField(verbose_name='Сумма оренды', default=0.0)
    deposit = models.FloatField(verbose_name='Залог', default=0.0)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name='Арендатор', blank=True, null=True)

    def day_rent_price(self):
        interval = self.interval().days
        if interval == 0:
            interval = 1
        return self.rent_amount / interval

    def day_rent_price_rounded(self):
        return round(self.day_rent_price(), 2)

    def current_return_many(self, end_date: datetime = now()):
        if self.end_time <= end_date or not self.my_break_rent:
            return 0
        dont_stop_date = self.start_time + timedelta(days=config.MIN_RENT)
        stop_date = dont_stop_date if end_date <= dont_stop_date else end_date
        delta = (self.end_time - stop_date).days
        if delta <= 0:
            return 0
        day_price = self.day_rent_price()
        return round(delta * day_price, 2)

    @property
    def return_many(self):
        return trunc(self.current_return_many() * 100)

    @property
    def return_deposit(self):
        return trunc(self.deposit * 100)

    def __str__(self):
        start_date_formtted = self.start_time.strftime('%d.%m.%y %H:%M:%S') if self.start_time else '--'
        end_date_formtted = self.end_time.strftime('%d.%m.%y %H:%M:%S') if self.end_time else '--'
        return f'{self.car.name} {self.rent_amount} от {start_date_formtted} до {end_date_formtted} ' \
               f'{self.current_return_many()} {self.deposit}'

    class Meta:
        verbose_name = 'Аренда авто'
        verbose_name_plural = 'Расписание аренды авто'
