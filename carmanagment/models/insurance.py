import math

from audit_log.models import CreatingUserField
from django.core.exceptions import ValidationError
from django.db import models

from balance.services import Balance
from carmanagment.models import Car, Counterpart


class CarInsurance(models.Model):
    car = models.ForeignKey(Car, verbose_name='Машина', on_delete=models.CASCADE)
    start_date = models.DateField(auto_created=True, verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата завершения')
    car_amount = models.FloatField(verbose_name='Страховой взнос', default=0)
    franchise = models.PositiveIntegerField(verbose_name='Франшиза', default=0)
    insurer = models.ForeignKey(Counterpart, verbose_name='Страховщик', on_delete=models.CASCADE)
    is_capital_expense = models.BooleanField(verbose_name='Покрытие капитальных затрат', default=0)
    created_by = CreatingUserField(related_name="created_insurance")

    def clean(self):
        if self.end_date is None or self.start_date is None:
            raise ValidationError('Start Date and end date is required')
        if self.end_date <= self.start_date:
            raise ValidationError('Start date need be less then End date')
        if self.car_amount <= 0:
            raise ValidationError('amount need be great then zero')
        super().clean()

    def validate_unique(self, exclude=None):
        qs = CarInsurance.objects.filter(car=self.car)
        if self.end_date is None or self.start_date is None:
            raise ValidationError('Start Date and end date is required')
        if qs.filter(start_date__gte=self.start_date).exists():
            raise ValidationError('The Car is already insured')
        if qs.filter(end_date__gte=self.end_date).exists():
            raise ValidationError('The Car is already insured')
        if qs.filter(start_date__lt=self.start_date, end_date__gte=self.start_date).exists():
            raise ValidationError('The Car is already insured')
        if qs.filter(start_date__lt=self.start_date, end_date__gte=self.end_date).exists():
            raise ValidationError('The Car is already insured')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        add_monay = self.pk is None
        super().save(force_insert, force_update, using, update_fields)
        if add_monay:
            Balance.form_transaction(Balance.INSURANCE, [
                (self.car.car_investor, self.insurer, math.trunc(self.car_amount * 100),
                 'Капитальные затрата на автомобиль'),
            ], "Страховой взнос")

    class Meta:
        verbose_name = 'Страховка'
        verbose_name_plural = 'Страховки'
        ordering = ['-start_date', '-end_date', 'insurer__name', 'car__name']

    def __str__(self):
        return f'{self.car.name} {self.insurer.name} от {self.start_date} до {self.end_date}'
