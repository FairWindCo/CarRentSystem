from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.
from balance.models import Account, Transaction


class CarBrand(models.Model):
    name = models.CharField(max_length=120, verbose_name='Бренд')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'


class CarModel(models.Model):
    name = models.CharField(max_length=120, verbose_name='Модель')
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.brand.name} {self.name}'

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'


class Investor(Account):
    profit = models.FloatField(verbose_name='Коифициент распределения прибыли')

    class Meta:
        verbose_name = 'Инвестор'
        verbose_name_plural = 'Инвесторы'


class Driver(Account):
    profit = models.FloatField(default=0.5, verbose_name='Коифициент распределения прибыли')

    class Meta:
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водители'


class Counterpart(Account):
    class Meta:
        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагенты'


class InvestmentCarBalance(Account):
    create_date = models.DateField(auto_created=True)

    class Meta:
        verbose_name = 'Инвестор'
        verbose_name_plural = 'Инвесторы'


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
    timestamp = models.DateTimeField(auto_now_add=True, auto_created=True, verbose_name='Дата начала поездки')
    mileage = models.PositiveIntegerField(verbose_name='Пробег по трекеру')
    fuel = models.PositiveIntegerField(verbose_name='Затраты на топливо')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='Водитель, если известно')
    amount = models.PositiveBigIntegerField(verbose_name='Сумма оплаты')
    car_amount = models.PositiveBigIntegerField(verbose_name='Сумма прибыли по машине')
    payer = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True,
                              verbose_name='Плательщик/От кого приняли средства', related_name='trips')
    cash = models.BooleanField(verbose_name='Оплата наличными')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)


class ExpensesTypes(models.Model):
    class ExpensesTypesClassify(models.IntegerChoices):
        CAR_EXPENSE = 1, 'Затраты на автомобиль'
        CAPITAL_CAR_EXPENSE = 2, 'Капитальные затраты на автомобиль'
        OTHER = 100, 'Прочее'

    name = models.CharField(max_length=250)
    type_class = models.PositiveSmallIntegerField(choices=ExpensesTypesClassify.choices,
                                                  verbose_name='Класс затрат',
                                                  default=ExpensesTypesClassify.OTHER)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Тип затрат'
        verbose_name_plural = 'Типы затрат'


class Expenses(models.Model):
    date_mark = models.DateTimeField(auto_now_add=True, auto_created=True)
    amount = models.PositiveBigIntegerField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_expenses')
    counterpart = models.ForeignKey(Counterpart, on_delete=models.CASCADE, related_name='counterpart_expenses')
    description = models.TextField()
    expenseType = models.ForeignKey(ExpensesTypes, on_delete=models.CASCADE)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='expense')

    def __str__(self):
        return f'FROM:{self.account.name} TO:{self.counterpart.name} ' \
               f'{self.amount}{self.account.get_currency()} - {self.expenseType.name}'

    class Meta:
        verbose_name = 'Затрата'
        verbose_name_plural = 'Затраты'
