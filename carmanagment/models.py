from django.db import models

# Create your models here.
from balance.models import Account


class CarBrand(models.Model):
    name = models.CharField(max_length=120, verbose_name='Бренд')

    def __str__(self):
        return f'{self.name}'


class CarModel(models.Model):
    name = models.CharField(max_length=120, verbose_name='Модель')
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.brand.name} {self.name}'


class Investor(Account):
    name = models.CharField(max_length=250, verbose_name='Имя')
    profit = models.FloatField()


class Driver(Account):
    name = models.CharField(max_length=250, verbose_name='Имя')


class Car(Account):
    name = models.CharField(max_length=250, verbose_name='Номер')
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    investor = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(max_length=4)
    mileage_at_start = models.PositiveIntegerField(verbose_name='')
    date_start = models.DateField(auto_now_add=True, auto_created=True)
    mileage = models.PositiveIntegerField(verbose_name='')
    last_TO_date = models.DateField(null=True)
    wialon_id = models.CharField(max_length=50, verbose_name='ID в системе WIALON')

    def __str__(self):
        return f'{self.model.brand.name} {self.model.name} {self.name}'


class Trip(models.Model):
    start = models.DateTimeField(auto_now_add=True, auto_created=True)
    end = models.DateTimeField()
    mileage = models.PositiveIntegerField(verbose_name='')
    fuel = models.PositiveIntegerField(verbose_name='')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)