import math
from datetime import timedelta

from django.contrib.admin import ModelAdmin, widgets
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Model, Q
from django.forms import fields, Form, ModelChoiceField, Select, \
    NumberInput, CheckboxInput, ModelMultipleChoiceField, CheckboxSelectMultiple
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from formtools.wizard.views import SessionWizardView

from balance.models import CashBox
from balance.services import Balance
from car_management.models import Car, Driver, TimeType, RentTerms
from car_management.models.rent_price import StatisticsType, PaidType
from car_rent.models import CarSchedule, CarsInOperator
from django_helpers.admin import CustomModelPage, CustomPageModelAdmin
from django_helpers.admin.ajax_select import AutocompleteSelectProxy
from django_helpers.admin.custom_ import CustomFormForAdminSite
from django_helpers.admin.custom_admin_page import CustomizeAdmin


class OperatorsForm(Form):
    taxi_in_operators = ModelMultipleChoiceField(
        queryset=CarsInOperator.objects.all(),
        widget=CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        # print('init OperatorsForm', args, kwargs)
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs:
            ids = kwargs['initial'].get('car_in_rents', None)
            if ids:
                self.fields['taxi_in_operators'].queryset = CarsInOperator.objects.filter(car__id=int(ids))


class TermsForm(Form):
    profit = fields.FloatField(initial=50, label='Процент распределения прибыли', widget=NumberInput())
    fuel_compensation = fields.FloatField(initial=100, label='Процент компенсации топлива', widget=NumberInput())
    additional_millage = fields.IntegerField(label='Дополнительный километраж на поездку', initial=4,
                                             widget=NumberInput())
    min_trips = fields.IntegerField(label='Минимальное количество поездок', initial=3, widget=NumberInput())
    max_millage = fields.IntegerField(label='Макс км за интервал', initial=2000, widget=NumberInput())
    plan_amount = fields.FloatField(label='План по кассе', initial=2500, widget=NumberInput())
    trips_control = fields.BooleanField(label='Контроль за количеством поездок', widget=CheckboxInput(), initial=True,
                                        required=False)
    millage_control = fields.BooleanField(label='Контроль за километражем', widget=CheckboxInput(), initial=True,
                                          required=False)
    amount_control = fields.BooleanField(label='Контроль за суммой кассы', widget=CheckboxInput(), initial=False,
                                         required=False)
    type_class = fields.ChoiceField(choices=TimeType.choices,
                                    label='Тип учета',
                                    initial=TimeType.DAYS)
    control_interval = fields.IntegerField(label='Контрольный интервал', initial=7, widget=NumberInput())
    control_interval_paid_distance = fields.IntegerField(label='Оплата за интервал', initial=1, widget=NumberInput())

    def __init__(self, *args, **kwargs):
        # print('init TermsForm', args, kwargs)
        super().__init__(*args, **kwargs)


class CashForm(Form):
    price = fields.FloatField(label='Тариф', widget=NumberInput(), initial=600)
    deposit_price = fields.FloatField(label='Залог', widget=NumberInput(), initial=4200, required=True)
    paid_deposit_price = fields.FloatField(label='Оплата залога', widget=NumberInput(), initial=4200, required=True)
    rent_cashbox = ModelChoiceField(label='Касса за аренду', queryset=CashBox.objects.all(), widget=Select)
    deposit_cashbox = ModelChoiceField(label='Депозит', queryset=CashBox.objects.all(), widget=Select, required=True)
    can_break_rent = fields.BooleanField(label='Разрешен досочный возврат', initial=True, widget=CheckboxInput(),
                                         required=False)
    statistics_type = fields.ChoiceField(choices=StatisticsType.choices, initial=StatisticsType.TRIP_STAT_DAY_PAID,
                                         label='Тип собираемой статистики')
    paid_type = fields.ChoiceField(choices=PaidType.choices, initial=PaidType.NO_TRANSACTION,
                                   label='Тип проводимых платежей')

    min_time = fields.IntegerField(label='Минимальный срок аренды', initial=0)

    def __init__(self, *args, **kwargs):
        print('init CashForm', args, kwargs)
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs:
            taxi = kwargs['initial'].get('in_taxi', False)
            statistics_type = kwargs['initial'].get('statistics_type', None)
            paid_type = kwargs['initial'].get('paid_type', None)
            self.fields['statistics_type'].initial = statistics_type
            self.fields['paid_type'].initial = paid_type
            if taxi:
                self.fields['price'].required = False
                self.fields['price'].initial = 0
                self.fields['price'].disabled = True

                self.fields['rent_cashbox'].required = False
                self.fields['rent_cashbox'].initial = None
                self.fields['rent_cashbox'].disabled = True


class CarSelectForm(CustomFormForAdminSite):
    work_in_taxi = fields.BooleanField(label='Работает в нашем такси', initial=False, widget=CheckboxInput,
                                       required=False)
    car = ModelChoiceField(label='Машина', queryset=Car.objects.all(), required=True,
                           widget=AutocompleteSelectProxy(field_name='car', model_name='carinrentpage',
                                                          app_label='car_rent',
                                                          to_field_name='account_ptr_id'))
    driver = ModelChoiceField(label='Водитель', queryset=Driver.objects.all(), required=True,
                              widget=AutocompleteSelectProxy(field_name='driver', model_name='carinrentpage',
                                                             app_label='car_rent',
                                                             to_field_name='account_ptr_id'))
    start_date = fields.SplitDateTimeField(widget=widgets.AdminSplitDateTime, initial=now())
    end_date = fields.SplitDateTimeField(widget=widgets.AdminSplitDateTime, initial=(now() + timedelta(days=7)),
                                         required=False)

    def clean(self):
        super().clean()
        start_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data['end_date']
        if end_date is not None and start_date > end_date:
            raise ValidationError(_('Дата начала периода больше даты завершени'))
        if 'car' in self.cleaned_data:
            car = self.cleaned_data['car']
            if end_date is not None:
                if CarSchedule.objects.filter(car=car). \
                        filter(Q(start_time__lte=start_date, end_time__gte=start_date) |
                               Q(start_time__lte=end_date, end_time__gte=end_date)).exists():
                    raise ValidationError(_('На этот период машина уже арендована'))
            else:
                if CarSchedule.objects.filter(car=car). \
                        filter(Q(start_time__lte=start_date, end_time__gte=start_date)).exists():
                    raise ValidationError(_('На этот период машина уже арендована'))
        pass


class AdminModelFormWrapper:

    def __init__(self, model: Model) -> None:
        super().__init__()
        self.model = model
        self.admin_view = ModelAdmin(model, None)

    def get_form(self, request, change=None):
        self.admin_view.get_form(request, None, change)


class CombyneWizard(SessionWizardView):
    form_list = [CarSelectForm, TermsForm, CashForm, OperatorsForm]

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
        driver = form_list[0].cleaned_data['driver']

        rent_term = RentTerms.from_dict_compare_create(driver.default_terms, form_list[1].cleaned_data, '_auto')

        price = form_list[2].cleaned_data['price']
        deposit_price = form_list[2].cleaned_data['deposit_price']
        paid_deposit_price = form_list[2].cleaned_data['paid_deposit_price']

        work_in_taxi = form_list[0].cleaned_data.get('work_in_taxi', False)
        min_time = form_list[2].cleaned_data.get('min_time', 0)

        trip_many_paid = form_list[2].cleaned_data.get('trip_many_paid', False)
        auto_renew = form_list[2].cleaned_data.get('auto_renew', False)

        rent_cashbox = form_list[2].cleaned_data['rent_cashbox']
        deposit_cashbox = form_list[2].cleaned_data['deposit_cashbox']

        taxi_in_operators = form_list[3].cleaned_data['taxi_in_operators']

        amount = math.trunc(price * 100)
        deposit = math.trunc(paid_deposit_price * 100)

        cash_box_deposit = deposit_cashbox if deposit_cashbox is not None else rent_cashbox
        with transaction.atomic():
            car_scheduler = CarSchedule(car=car, start_time=start_date, end_time=end_date,
                                        term=rent_term,
                                        paid_deposit=round(paid_deposit_price, 2),
                                        deposit=round(deposit_price, 2),
                                        amount=round(price, 2),
                                        driver=driver,
                                        auto_renew=auto_renew,
                                        work_in_taxi=work_in_taxi,
                                        min_time=min_time,
                                        statistics_type=form_list[2].cleaned_data['statistics_type'],
                                        paid_type=form_list[2].cleaned_data['paid_type'],
                                        )
            car_scheduler.save()
            car_scheduler.taxi_operators.set(taxi_in_operators)
            car_scheduler.save()

            operations = [
                (None, cash_box_deposit, deposit, f'Залог за аренду {car.name}'),
            ]
            if amount > 0 and rent_cashbox:
                operations.extend(
                    [(None, rent_cashbox, amount, f'Деньги за аренду {car.name}'),
                     (None, car, amount, f'Деньги за аренду {car.name}'),
                     ]
                )
            Balance.form_transaction(Balance.DEPOSIT, operations, 'Аренда автомобиля')

    def get_form(self, step=None, data=None, files=None):
        return super().get_form(step, data, files)

    def get_form_instance(self, step):
        form_element = super().get_form_instance(step)
        return form_element

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        return context

    def get_form_initial(self, step):
        int_step = int(step)
        if int_step >= 1:
            cleaned = self.get_cleaned_data_for_step('0')
            in_taxi = cleaned.get('work_in_taxi', False)
            if 'end_date' in cleaned and cleaned['end_date']:
                delta = cleaned['end_date'] - cleaned['start_date']
            else:
                delta = 0
            car = cleaned['car']
            driver = cleaned['driver']

            self.initial_dict['3'] = {
                'car_in_rents': car.id,
            }
            if driver.default_terms:
                self.initial_dict['1'] = driver.default_terms.to_dict_m()
            if car.rent_price_plan:
                deposit = car.rent_price_plan.get_deposit(delta)
                self.initial_dict['2'] = {
                    'price': car.rent_price_plan.get_price(delta),
                    'deposit_price': deposit,
                    'paid_deposit_price': deposit,
                    'in_taxi': in_taxi,
                    'statistics_type': car.rent_price_plan.statistics_type,
                    'paid_type': car.rent_price_plan.paid_type,
                }
            else:
                self.initial_dict['2'] = {
                    'in_taxi': in_taxi
                }
        if int_step >= 3:
            cleaned = self.get_cleaned_data_for_step('0')
            car = cleaned['car']
            self.initial_dict['3'] = {
                'car_in_rents': car.id,
            }
        print('INITIAL DICT', self.initial_dict)
        return super().get_form_initial(step)


class RentPageModelAdmin(CustomModelPage):
    title = 'Машини в аренде'

    class Meta:
        app_label = 'car_rent'


class CarRentAdmin(CustomizeAdmin):
    title = 'wizard'
    app_label = 'car_rent'
    custom_add_view = CombyneWizard
    search_fields = ('car__name',)
    list_display = ('car', 'start_time', 'end_time', 'driver',)
    list_filter = ('car__name',)

    def has_change_permission(self, request, obj=None):
        return True

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return 'car', 'start_time', 'end_time', 'driver', 'end_rent', \
                   'taxi_operators', 'deposit', 'paid_deposit', 'amount', 'min_time', 'can_break_rent'
        else:
            return []

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
