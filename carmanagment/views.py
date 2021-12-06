# Create your views here.
import json
from datetime import timedelta

from django import forms
from django.shortcuts import render
from django.utils.timezone import now
from django.views.generic import ListView
from vue_utils.views import FilterListView

from balance.models import AccountTransaction, Transaction
from carmanagment.models import TaxiTrip, Car, Expenses, Investor, Driver, TaxiOperator, Counterpart, TripStatistics
from carmanagment.serivices.statisrics_service import Statistics
from django_request_processor.django_list_view import UniversalFilterListView
from main_menu.views import MainMenuView


class ViewTrips(FilterListView):
    model = TaxiTrip
    template_name = 'carmanagment/trip_list.html'
    paginate_by = 20
    filters_fields = (
        ('car__name', 'icontains', None, None, False, False),
        ('timestamp__gte', None, 'start_interval'),
        ('timestamp__lte', None, 'end_interval'),
    )


class ByCarView(ListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.current_car = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        cars = Car.objects.order_by('name').all()
        context['cars'] = cars
        context['current_car'] = self.current_car
        return context

    def get(self, request, *args, **kwargs):
        if 'car_name' in kwargs:
            try:
                self.current_car = Car.objects.get(name=kwargs['car_name'])
            except Car.DoesNotExist:
                pass

        return super().get(request, *args, **kwargs)


class GlobalMainMenu(MainMenuView):
    main_menu = {
        'DashBoard': {
            'icon': 'grid-fill',
            'view': 'dashboard',
            # 'user': 'admin'
        },
        'Финансы': {
            'group': 'anon'
        },
        'Балансы': {
            'icon': 'grid-fill',
            'submenu': {
                'Машин': {
                    'view': 'cars',
                    'icon': 'card',
                },
                'Ивест.': {
                    'view': 'invest',
                },
                'Водители': {
                    'view': 'drivers',
                },
                'Патнеры': {
                    'view': 'investors',
                },
                'Контрагенты': {
                    'view': 'counterparts',
                },
                'Операторы': {
                    'view': 'taxi_operators',
                },
            }
        },
        'Поездки': {
            'view': 'all_trips',
            'icon': 'map',
        },
        'Затраты': {
            'view': 'all_expenses',
            'icon': 'bag',
        },
        'Средства': {
            'icon': 'credit-card',
            'submenu': {
                'Транзакции': {
                    'view': 'all_transactions',
                },
                'Операции': {
                    'view': 'all_operations',
                },
            },
        },
        'Статистика': {
            'submenu': {
                'Статистика': {
                    'view': 'trip_stat',
                },
            }
        },
        'Отчеты': {
            'submenu': {
                'Отчет по авто': {
                    'view': 'car_report',
                },
            }
        },
    }


class ViewCarTrips(UniversalFilterListView, ByCarView, GlobalMainMenu):
    model = TaxiTrip
    template_name = 'carmanagment/cars_trip_list.html'
    paginate_by = 20
    ordering = ('-timestamp',)
    filtering = (
        ('car__name',),
        ('timestamp__gte', 'start_interval'),
        ('timestamp__lte', 'end_interval'),
    )

    def get_queryset(self):
        if self.current_car:
            self.queryset = TaxiTrip.objects.filter(car=self.current_car).all()
        return super().get_queryset()


class ViewCarAccount(UniversalFilterListView, GlobalMainMenu):
    model = Car
    template_name = 'carmanagment/acccount_list.html'
    paginate_by = 20
    filtering = (
        ('name',),
    )


class ViewCarInvestmentAccount(ViewCarAccount, GlobalMainMenu):
    model = Car
    template_name = 'carmanagment/inest_list.html'
    paginate_by = 20
    filtering = (
        ('name',),
    )


class ViewInvestorAccount(ViewCarAccount, GlobalMainMenu):
    model = Investor


class ViewDriverAccount(ViewCarAccount, GlobalMainMenu):
    model = Driver


class ViewCounterpartAccount(ViewCarAccount, GlobalMainMenu):
    model = Counterpart


class ViewTaxiOperatorAccount(ViewCarAccount, GlobalMainMenu):
    model = TaxiOperator


class ViewCarExpenses(UniversalFilterListView, ByCarView, GlobalMainMenu):
    model = Expenses
    template_name = 'carmanagment/cars_expenses_list.html'
    paginate_by = 20
    ordering = ('-date_mark',)
    filtering = (
        ('account__name__icontains', 'name'),
        ('date_mark__gte', 'start_interval'),
        ('date_mark__lte', 'end_interval'),
    )

    def get_queryset(self):
        if self.current_car:
            self.queryset = Expenses.objects.filter(account=self.current_car)
        else:
            self.queryset = Expenses.objects.filter(account__pk__in=Car.objects.values('pk').all())
        return super().get_queryset()


class OperationsView(UniversalFilterListView, GlobalMainMenu):
    model = AccountTransaction
    template_name = 'carmanagment/operation_list.html'
    paginate_by = 20
    filtering = (
        ('account__name__icontains', 'name'),
        ('transaction__transactionTime__gte', 'start_interval'),
        ('transaction__transactionTime__lte', 'end_interval'),
    )


class TransactionView(UniversalFilterListView, GlobalMainMenu):
    model = Transaction
    template_name = 'carmanagment/transaction_list.html'
    paginate_by = 20
    filtering = (
        ('transactionTime__gte', 'start_interval'),
        ('transactionTime__lte', 'end_interval'),
    )


class ViewTripsNew(UniversalFilterListView, GlobalMainMenu):
    model = TaxiTrip
    template_name = 'carmanagment/trip_list.html'
    paginate_by = 20
    use_custom_order = True
    return_json_as_response = True
    serialize = (
        ('timestamp', None, 'str_datetime_%d.%m.%Y %H:%M:%S', 'special'),
    )
    filtering = (
        ('car__name',),
        ('timestamp__gte', 'start_interval'),
        ('timestamp__lte', 'end_interval'),
    )


class ViewTripsNew2(UniversalFilterListView, GlobalMainMenu):
    model = TaxiTrip
    template_name = 'carmanagment/trip_list.html'
    use_custom_paging = False
    paginate_by = 20
    filters = (
        ('car__name',),
        ('timestamp__gte', 'start_interval'),
        ('timestamp__lte', 'end_interval'),
    )


def test_view(request):
    return render(request, 'admin_template/base_template.html', {})


class ViewCarStatistic(UniversalFilterListView, ByCarView, GlobalMainMenu):
    model = TripStatistics
    template_name = 'carmanagment/cars_stat_list.html'
    paginate_by = 20
    ordering = ('-stat_date',)
    filtering = (
        ('car__name',),
        ('stat_date__gte', 'start_interval'),
        ('stat_date__lte', 'end_interval'),
    )

    def get_queryset(self):
        if self.current_car:
            self.queryset = TripStatistics.objects.filter(car=self.current_car).all()
        return super().get_queryset()


def dashboard(request):
    import random

    def getRandomCol():

        r = hex(random.randrange(0, 16))[2:] + hex(random.randrange(0, 16))[2:]
        g = hex(random.randrange(0, 255))[2:] + hex(random.randrange(0, 16))[2:]
        b = hex(random.randrange(0, 255))[2:] + hex(random.randrange(0, 16))[2:]

        random_col = '#' + r[:2] + g[:2] + b[:2]
        return random_col

    context = GlobalMainMenu.form_menu_context(request)
    trip_stat = Statistics.get_last_statistics()
    context['page_header'] = 'DashBoard'
    trip_data = []
    trip_sum = []
    trip_label = []
    trip_color = []
    for index, (name, stats) in enumerate(trip_stat.items()):
        trip_data.append(
            {'name': name,
             'data': [el.trip_count for el in stats]})
        trip_sum.append(
            {'name': name,
             'data': [el.amount for el in stats]})
        trip_color.append(getRandomCol())
        if index == 0:
            trip_label = [el.stat_date.strftime('%d.%m.%y') for el in stats]

    context['trips_data'] = trip_data
    context['trips_sum'] = trip_sum
    context['cars'] = json.dumps(trip_label)
    context['colors'] = json.dumps(trip_color)
    return render(request, 'admin_template/dashboard.html', context)


class CarReportForm(forms.Form):
    start_date = forms.DateField(label='Дата начала периода', widget=forms.DateInput(format='%Y-%m-%d'),
                                 initial=(now() - timedelta(days=7)).date().strftime('%Y-%m-%d'))
    end_date = forms.DateField(label='Дата конца периода', widget=forms.DateInput(format='%Y-%m-%d'),
                               initial=(now()).date().strftime('%Y-%m-%d'))
    car = forms.ModelChoiceField(label='Машина', queryset=Car.objects.all(),
                                 widget=forms.Select(attrs={'class': 'form-control round'}))


def car_usage_report(request):
    context = GlobalMainMenu.form_menu_context(request)
    cars_trips_stat = []
    expenses = []
    total_rent, total_fuel, total_trip, expense_amount = 0, 0, 0, 0
    total_millage, total_car_amount, total_driver, total_payer_amount = 0, 0, 0, 0
    full_total_payer_amount = 0
    total_bank = 0
    firm_rent = 0
    if request.method == 'POST':
        form = CarReportForm(request.POST)
        if form.is_valid():
            cars_trips_stat = TripStatistics.objects.filter(
                stat_date__lte=form.cleaned_data['end_date'],
                stat_date__gte=form.cleaned_data['start_date'],
                car=form.cleaned_data['car']).all()
            for trip_stat in cars_trips_stat:
                total_rent += trip_stat.amount
                total_fuel += trip_stat.fuel
                total_trip += trip_stat.trip_count
                total_millage += trip_stat.mileage
                total_car_amount += trip_stat.car_amount
                total_driver += trip_stat.driver_amount
                total_payer_amount += trip_stat.payer_amount
                full_total_payer_amount += trip_stat.total_payer_amount
                total_bank += trip_stat.total_bank_rent
                firm_rent += trip_stat.total_firm_rent

            expenses = Expenses.objects.filter(account=form.cleaned_data['car'],
                                               date_mark__lte=form.cleaned_data['end_date'],
                                               date_mark__gte=form.cleaned_data['start_date']
                                               ).all()
            expense_amount = sum(expense.amount for expense in expenses)
    else:
        form = CarReportForm()

    context['form'] = form
    context['object_list'] = cars_trips_stat
    context['expenses'] = expenses
    context['total'] = {
        'amount': total_rent,
        'fuel': total_fuel,
        'trip': total_trip,
        'mileage': total_millage,
        'car_amount': total_car_amount,
        'driver_amount': total_driver,
        'payer_amount': total_payer_amount,
        'expense_amount': expense_amount,
        'total_sum': total_car_amount - expense_amount,
        'full_total_payer_amount': full_total_payer_amount,
        'total_bank':total_bank,
        'firm_rent': firm_rent,
    }
    return render(request, 'carmanagment/car_report.html', context)
