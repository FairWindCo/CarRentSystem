import math
from datetime import timedelta

from django.contrib.admin import ModelAdmin, widgets
from django.contrib.admin.widgets import AutocompleteSelect
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Model, Q
from django.forms import fields, Form, EmailInput, ModelChoiceField, DateInput, SelectDateWidget, Media, Select, \
    NumberInput
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.timezone import now
from formtools.wizard.views import SessionWizardView
from django.utils.translation import gettext_lazy as _
from balance.models import CashBox
from balance.services import Balance
from django_helpers.admin.ajax_select import AutocompleteSelectProxy
from django_helpers.admin.custom_ import CustomFormForAdminSite
from django_helpers.admin.custom_admin_page import CustomizeAdmin
from django_helpers.admin import CustomModelPage, CustomPageModelAdmin
from carmanagment.models import CarSchedule, Car, Driver
from django_helpers.admin.utility_classes import MyCl


class CashForm(Form):
    price = fields.FloatField(label='Тариф', widget=NumberInput())
    deposit_price = fields.FloatField(label='Залог', widget=NumberInput())
    paid_deposit_price = fields.FloatField(label='Оплата залога', widget=NumberInput())
    rent_cashbox = ModelChoiceField(label='Касса за аренду', queryset=CashBox.objects.all(), widget=Select)
    deposit_cashbox = ModelChoiceField(label='Депозит', queryset=CashBox.objects.all(), widget=Select, required=False)
    driver = ModelChoiceField(label='Водитель', queryset=Driver.objects.all(), widget=Select, required=False)


class CarSelectForm(CustomFormForAdminSite):
    car = ModelChoiceField(label='Машина', queryset=Car.objects.filter(rent_price_plan__isnull=False).all(),
                           widget=AutocompleteSelectProxy(field_name='car', model_name='carinrentpage',
                                                          app_label='carrent',
                                                          to_field_name='account_ptr_id'))
    start_date = fields.SplitDateTimeField(widget=widgets.AdminSplitDateTime, initial=now())
    end_date = fields.SplitDateTimeField(widget=widgets.AdminSplitDateTime, initial=(now() + timedelta(days=7)))

    def clean(self):
        super().clean()
        start_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data['end_date']
        if start_date > end_date:
            raise ValidationError(_('Дата начала периода больше даты завершени'))
        car = self.cleaned_data['car']
        if CarSchedule.objects.filter(car=car). \
                filter(Q(start_time__lte=start_date, end_time__gte=start_date) |
                       Q(start_time__lte=end_date, end_time__gte=end_date)).exists():
            raise ValidationError(_('На этот период машина уже арендована'))


class AdminModelFormWrapper:

    def __init__(self, model: Model) -> None:
        super().__init__()
        self.model = model
        self.admin_view = ModelAdmin(model, None)

    def get_form(self, request, change=None):
        self.admin_view.get_form(request, None, change)


class CombyneWizard(SessionWizardView):
    form_list = [CarSelectForm, CashForm]

    @property
    def __name__(self):
        return self.__class__.__name__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = None

    def done(self, form_list, **kwargs):
        car = form_list[0].cleaned_data['car']
        start_date = form_list[0].cleaned_data['start_date']
        end_date = form_list[0].cleaned_data['end_date']
        price = form_list[1].cleaned_data['price']
        deposit_price = form_list[1].cleaned_data['deposit_price']
        paid_deposit_price = form_list[1].cleaned_data['paid_deposit_price']
        rent_cashbox = form_list[1].cleaned_data['rent_cashbox']
        deposit_cashbox = form_list[1].cleaned_data['deposit_cashbox']
        driver = form_list[1].cleaned_data['driver']
        amount = math.trunc(price * 100)
        deposit = math.trunc(paid_deposit_price * 100)
        cash_box_deposit = deposit_cashbox if deposit_cashbox is not None else rent_cashbox
        with transaction.atomic():
            car_scheduler = CarSchedule(car=car, start_time=start_date, end_time=end_date,
                                        paid_deposit=round(paid_deposit_price, 2),
                                        deposit=round(deposit_price, 2),
                                        amount=round(price, 2),
                                        driver=driver, price=car.rent_price_plan
                                        )
            car_scheduler.save()
            Balance.form_transaction(Balance.DEPOSIT, [
                (None, rent_cashbox, amount, f'Деньги за аренду {car.name}'),
                (None, cash_box_deposit, deposit, f'Залог за аренду {car.name}'),
                (None, car, amount, f'Деньги за аренду {car.name}'),
            ], 'Аренда автомобиля')

    def get_form(self, step=None, data=None, files=None):
        return super().get_form(step, data, files)

    def get_form_instance(self, step):
        form_element = super().get_form_instance(step)
        return form_element

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        return context

    def get_form_initial(self, step):
        if step == '1':
            cleaned = self.get_cleaned_data_for_step('0')
            delta = cleaned['end_date'] - cleaned['start_date']
            car = cleaned['car']

            print(cleaned)
            deposit = car.rent_price_plan.get_deposit(delta)
            self.initial_dict['1'] = {
                'price': car.rent_price_plan.get_price(delta),
                'deposit_price': deposit,
                'paid_deposit_price': deposit,
            }
        return super().get_form_initial(step)


class RentPageModelAdmin(CustomModelPage):
    title = 'Машини в аренде'

    class Meta:
        app_label = 'carrent'


class CarRentAdmin(CustomizeAdmin):
    title = 'wizard'
    app_label = 'carrent'
    custom_add_view = CombyneWizard
    search_fields = ('car__name',)
    list_display = ('car', 'start_time', 'end_time', 'driver',)
    list_filter = ('car__name',)

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return CarSchedule.objects.all()



class Additiona(CustomPageModelAdmin):
    autocomplete_fields = ('car',)

    def get_form(self, request, obj=None, change=False, **kwargs):
        print('fpr')
        return super().get_form(request, obj, change, **kwargs)

    def _changeform_view(self, request, object_id, form_url, extra_context):
        m = super()._changeform_view(request, object_id, form_url, extra_context)
        print(m)
        return m
