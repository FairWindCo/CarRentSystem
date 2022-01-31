import math
from datetime import timedelta

from django.contrib.admin import ModelAdmin, widgets
from django.contrib.admin.widgets import AutocompleteSelect
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Model, Q
from django.forms import fields, Form, EmailInput, ModelChoiceField, DateInput, SelectDateWidget, Media, Select, \
    NumberInput
from django.forms.widgets import Input
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.timezone import now
from formtools.wizard.views import SessionWizardView
from django.utils.translation import gettext_lazy as _
from balance.models import CashBox
from balance.services import Balance
from car_rent.models import CarSchedule
from django_helpers.admin.ajax_select import AutocompleteSelectProxy
from django_helpers.admin.custom_ import CustomFormForAdminSite
from django_helpers.admin.custom_admin_page import CustomizeAdmin
from django_helpers.admin import CustomModelPage, CustomPageModelAdmin
from car_management.models import Car, Driver
from django_helpers.admin.utility_classes import MyCl


class ReturnCashForm(Form):
    text = fields.CharField(label='Действие', initial='Возврат средств и депозита', widget=Input(attrs={'readonly': 'readonly'}))
    price = fields.FloatField(label='Тариф', widget=NumberInput(attrs={'readonly': 'readonly'}))
    deposit_price = fields.FloatField(label='Залог', widget=NumberInput(attrs={'readonly': 'readonly'}))
    deposit_cashbox = ModelChoiceField(label='Касса депозита', queryset=CashBox.objects.all(), widget=Select)
    rent_cashbox = ModelChoiceField(label='Касса', queryset=CashBox.objects.all(), widget=Select)


class ReturnDepositForm(Form):
    text = fields.CharField(label='Действие', initial='Возврат депозита', widget=Input(attrs={'readonly': 'readonly'}))
    deposit_price = fields.FloatField(label='Остаток залога', widget=NumberInput(attrs={'readonly': 'readonly'}))
    deposit_cashbox = ModelChoiceField(label='Касса', queryset=CashBox.objects.all(), widget=Select)


class PaidForm(Form):
    text = fields.CharField(label='Действие', initial='Доплата средств', widget=Input(attrs={'readonly': 'readonly'}))
    price = fields.FloatField(label='Доплата', widget=NumberInput(attrs={'readonly': 'readonly'}))
    deposit_cashbox = ModelChoiceField(label='Касса', queryset=CashBox.objects.all(), widget=Select)


class CarSchedulerSelectForm(CustomFormForAdminSite):
    car_rent = ModelChoiceField(label='Аренда', queryset=CarSchedule.objects.all(),
                                # widget=AutocompleteSelectProxy(field_name='car', model_name='carschedule',
                                #                                app_label='carmanagment',
                                #                                to_field_name='car_id')
                                )
    end_date = fields.SplitDateTimeField(widget=widgets.AdminSplitDateTime, initial=now())


class AdminModelFormWrapper:

    def __init__(self, model: Model) -> None:
        super().__init__()
        self.model = model
        self.admin_view = ModelAdmin(model, None)

    def get_form(self, request, change=None):
        self.admin_view.get_form(request, None, change)


def test_step_one(wizard):
    step = wizard.initial_dict.get('next_form', 'zero')
    res = step == 'one' or step == 'zero'
    print('one', res)
    return res


def test_step_two(wizard):
    step = wizard.initial_dict.get('next_form', 'zero')
    res = step == 'two' or step == 'zero'
    print('two', res)
    return res


def test_step_three(wizard):
    step = wizard.initial_dict.get('next_form', 'zero')
    res = step == 'three' or step == 'zero'
    print('three', res)
    return res


condition_tests = {
    '0': True,
    '1': test_step_one,
    '2': test_step_two,
    '3': test_step_three,
}


class CombyneWizard(SessionWizardView):
    form_list = [CarSchedulerSelectForm, ReturnCashForm, ReturnDepositForm, PaidForm]

    condition_dict = condition_tests

    @property
    def __name__(self):
        return self.__class__.__name__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = None

    def done(self, form_list, **kwargs):
        car_rent = form_list[0].cleaned_data['car_rent']
        end_date = form_list[0].cleaned_data['end_date']
        car = car_rent.car
        price, deposit = car_rent.current_return(end_date)

        deposit_cashbox = form_list[1].cleaned_data['deposit_cashbox']
        deposit_int = abs(round(deposit * 100))
        price_int = abs(round(price * 100))

        with transaction.atomic():
            car_rent.end_rent = end_date
            operations = []
            if price > 0 and car_rent.can_break_rent:
                rent_cashbox = form_list[1].cleaned_data['rent_cashbox']
                deposit_cashbox = deposit_cashbox if deposit_cashbox is not None else rent_cashbox
                operations.append((rent_cashbox, None, price_int, f'Выдача средств за досрочный возврат {car.name}'))
                operations.append((car, None, price_int, f'Досрочный возврат {car.name}'))
            if deposit > 0:
                operations.append((deposit_cashbox, None, deposit_int, f'Выдача залога {car.name}'))
            elif deposit < 0:
                operations.append((None, deposit_cashbox, deposit_int, f'Доплата {car.name}'))
                operations.append((None, car, price_int, f'Деньги за аренду {car.name}'))

            Balance.form_transaction(Balance.DEPOSIT, operations, 'Возврат залога за аренду автомобиля')
            car_rent.save()

    def get_form_instance(self, step):
        form_element = super().get_form_instance(step)
        return form_element

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        return context

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        if step is None and data and form.is_valid():
            car_rent = form.cleaned_data['car_rent']
            end_time = form.cleaned_data['end_date']
            price, deposit = car_rent.current_return(end_time)
            self.initial_dict['next_form'] = 'one'
            self.initial_dict['1'] = {
                'price': price,
                'deposit_price': deposit,
            }
            self.initial_dict['2'] = {
                'deposit_price': deposit,
            }
            self.initial_dict['3'] = {
                'price': deposit,
            }

            if price > 0:
                self.initial_dict['next_form'] = 'one'
            elif deposit > 0:
                self.initial_dict['next_form'] = 'two'
            else:
                self.initial_dict['next_form'] = 'three'
            print(self.initial_dict['next_form'])
        return form

    def get_form_initial(self, step):
        return super().get_form_initial(step)


class ReturnRentPageModelAdmin(CarSchedule):
    title = 'Машини в аренде'

    class Meta:
        proxy = True
        app_label = 'car_rent'


class ReturnCarRentAdmin(CustomizeAdmin):
    title = 'Возврат машины'
    model_title = 'Возврат машины'
    custom_add_view = CombyneWizard
    search_fields = ('car__name',)
    app_label = 'car_rent'

    # list_display = ('car', 'start_time', 'end_time', 'driver',)
    #  list_filter = ('car__name',)

    custom_change_view = True

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        return self.changeform_view(request, None)
