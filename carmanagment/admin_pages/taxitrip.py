from constance import config
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from balance.models import CashBox
from external_services.fuel_statisitics.django_fuel_config import get_special_fuel_help_text
from django_helpers.admin import CustomModelPage
from carmanagment.models import Car, Driver, TaxiOperator, TaxiTrip


class TaxiTripPage(CustomModelPage):
    title = 'Добавить поездку в Такси'  # set page title
    # Define some fields.
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Авто', related_name='taxi_car')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name='Водитель', related_name='taxi_driver')
    counterpart = models.ForeignKey(TaxiOperator, on_delete=models.CASCADE, verbose_name='Контрагент',
                                    related_name='taxi_service')
    amount = models.PositiveIntegerField(verbose_name='Сумма')
    millage = models.PositiveIntegerField(verbose_name='Растояние')
    gas_price = models.FloatField(verbose_name='Цена газа', help_text=get_special_fuel_help_text())
    cash = models.FloatField(verbose_name='Оплата наличными', default=0)
    start_time = models.DateTimeField(verbose_name='Дата и время начала поездки')
    cash_box = models.ForeignKey(CashBox, on_delete=models.CASCADE, verbose_name='Касса',
                                 related_name='trip_cash_box', blank=True, null=True)

    def clean(self):
        if config.FIRM is None:
            raise ValidationError('Need Set Firm account in Config')
        if not hasattr(self, 'car'):
            raise ValidationError(_('Машина обязательна'))
        if not hasattr(self, 'driver'):
            raise ValidationError(_('Водительн обязателен'))
        if not hasattr(self, 'counterpart'):
            raise ValidationError(_('Контрагент обязателен'))
        if hasattr(self, 'cash') and getattr(self, 'cash') and \
                (not hasattr(self, 'cash_box') or getattr(self, 'cash_box') is None):
            raise ValidationError(_('Для наличных средств обязательна касса'))
        super().clean()

    def save(self):
        if TaxiTrip.manual_create_taxi_trip(self.car, self.driver, self.start_time,
                                            self.counterpart, self.millage, self.amount,
                                            self.gas_price, self.cash, '', self.cash_box):
            self.bound_admin.message_success(self.bound_request, _('Поездка добавлена'))