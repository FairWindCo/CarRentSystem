from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from balance.models import Account
from carmanagment.models import Investor, InvestmentCarBalance


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

