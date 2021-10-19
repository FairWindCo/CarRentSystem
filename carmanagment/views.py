# Create your views here.
import json

from django.shortcuts import render
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

        r = hex(random.randrange(0, 16))[2:]+hex(random.randrange(0, 16))[2:]
        g = hex(random.randrange(0, 255))[2:]+hex(random.randrange(0, 16))[2:]
        b = hex(random.randrange(0, 255))[2:]+hex(random.randrange(0, 16))[2:]

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
