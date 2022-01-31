from django.db import models

from car_management.models import Car
from .taxi_operator import TaxiOperator


class CarsInOperator(models.Model):
    car = models.ForeignKey(Car, on_delete=models.PROTECT, related_name='cars_in_taxi', verbose_name='Машина')
    operator = models.ForeignKey(TaxiOperator, on_delete=models.CASCADE, related_name='taxi_park',
                                 verbose_name='Таксопарк')
    signal = models.CharField(max_length=7, verbose_name='Позывной', default='')
    car_uid = models.CharField(max_length=255, blank=True, null=True, verbose_name='Идентификатор машины')

    def __str__(self):
        return f'{self.operator.name} {self.car.name} {self.signal}'

    class Meta:
        verbose_name = 'Машины в таксопарках'
        verbose_name_plural = 'Машины в таксопарках'
        unique_together = (("operator", "signal"), ("operator", "car_uid"))
        ordering = ("car__name", "signal", "operator")

    @classmethod
    def find_car_by_uid(cls, operator: TaxiOperator, uid: str):
        try:
            car_in_operator = cls.objects.get(car_uid=uid, operator=operator)
            return car_in_operator.car
        except cls.DoesNotExist:
            return None

    @classmethod
    def find_car_by_signal(cls, operator: TaxiOperator, signal: str):
        try:
            car_in_operator = cls.objects.get(signal=signal, operator=operator)
            return car_in_operator.car
        except cls.DoesNotExist:
            return None
