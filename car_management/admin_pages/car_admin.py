from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from django_helpers.admin import CustomModelPage
from django_helpers.admin.artificial_admin_models import CustomPageModelAdmin
from car_management.models import Investor, CarModel
from car_management.serivices.car_service import CarCreator


class CarAdmin(admin.ModelAdmin):
    readonly_fields = (
        'currency', 'last_period_balance', 'car_investor', 'model', 'investment', 'date_start', 'name', 'year',
        'mileage_at_start', 'investment')
    ordering = ['name', 'model__name', 'model__brand__name']
    search_fields = ['name', 'model__name', 'model__brand__name', 'signal']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False


class CarInsuranceAdmin(admin.ModelAdmin):
    autocomplete_fields = ('car', 'insurer')

    def has_delete_permission(self, request: HttpRequest, obj: models.Model = None) -> bool:
        return False

    def has_change_permission(self, request, obj=None):
        return False


class CarModelAdmin(admin.ModelAdmin):
    ordering = ['brand__name', 'name']
    search_fields = ['brand__name', 'name']


class CarAddPageAdmin(CustomPageModelAdmin):
    autocomplete_fields = ('investor', 'car_model')


class CarInTaxiAdmin(admin.ModelAdmin):
    autocomplete_fields = ('car', 'driver', 'operator')


class CarAddPage(CustomModelPage):
    title = 'Подключить авто'  # set page title
    # Define some fields.
    car_plate = models.CharField(max_length=100, verbose_name='номе машины')
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, verbose_name='Ивестор')
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, verbose_name='Модель')
    car_signal = models.CharField(max_length=6, default='')
    year = models.PositiveIntegerField(verbose_name='Год выпуска', validators=[
        MaxValueValidator(2100),
        MinValueValidator(1900)
    ])
    millage = models.PositiveIntegerField(verbose_name='Пробег на текущий момент')
    amount = models.PositiveIntegerField(verbose_name='Сумма инвестиций')

    def clean(self):
        if not hasattr(self, 'investor') or self.investor is None:
            raise ValidationError(_('Ивестор обязателен'))
        if not hasattr(self, 'car_model') or self.car_model is None:
            raise ValidationError(_('Модель обязательна'))
        super().clean()

    def save(self):
        CarCreator.add_new_car(self.investor, self.car_model, self.car_plate, self.year, self.millage, self.amount,
                               self.car_signal)
        self.bound_admin.message_success(self.bound_request, _('Машина подключена'))
