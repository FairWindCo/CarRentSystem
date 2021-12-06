from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, F

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
        return cls.objects.filter(car=car).filter(
            Q(start_time__gte=date_time, end_time__lte=date_time)
        ).exists()

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
    fix_rent = models.BooleanField(verbose_name='Машина в аренде', default=True)
    rent_amount = models.PositiveIntegerField(verbose_name='Сумма оренды', default=0.0)
    deposit = models.PositiveIntegerField(verbose_name='Залог', default=0.0)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name='Арендатор', blank=True, null=True)

    def __str__(self):
        return f'{self.car.name} {self.rent_amount} от {self.start_time} до {self.end_time}'

    class Meta:
        verbose_name = 'Аренда авто'
        verbose_name_plural = 'Расписание аренды авто'
