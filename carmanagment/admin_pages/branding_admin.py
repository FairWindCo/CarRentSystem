from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from balance.models import CashBox
from carmanagment.models import Car
from carmanagment.models.taxi import BrandingAmount
from django_helpers.admin import CustomModelPage
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib import admin


class BrandingAddAdmin(admin.ModelAdmin):
    autocomplete_fields = ('car', 'cash_box')


class BrandingAddPage(CustomModelPage):
    title = 'Брендирование авто'  # set page title
    # Define some fields.
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Автомобиль')
    amount = models.FloatField(verbose_name='Оплата за брендирование', validators=[
        MinValueValidator(0)
    ])
    cash_box = models.ForeignKey(CashBox, on_delete=models.CASCADE, verbose_name='Касса',
                                 related_name='branding_cash_box_rel')

    def clean(self):
        if not hasattr(self, 'car') or self.car is None:
            raise ValidationError(_('Машина обязателен'))
        if not hasattr(self, 'cash_box') or self.cash_box is None:
            raise ValidationError(_('Касса обязательна'))
        super().clean()

    def save(self):
        branding = BrandingAmount.make_branding(self.car, self.amount)
        branding.make_transaction(self.cash_box)
        branding.save()

        self.bound_admin.message_success(self.bound_request, _('Доход за брендирование учтен'))
