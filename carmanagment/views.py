# Create your views here.
from django.shortcuts import render
from django.views.generic import ListView
from vue_utils.views import FilterListView

from balance.models import AccountTransaction, Transaction
from carmanagment.models import TaxiTrip, Car, Expenses, Investor, Driver, TaxiOperator, Counterpart
from django_request_processor.django_list_view import UniversalFilterListView


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


class ViewCarTrips(UniversalFilterListView, ByCarView):
    model = TaxiTrip
    template_name = 'carmanagment/cars_trip_list.html'
    paginate_by = 20
    filtering = (
        ('car__name',),
        ('timestamp__gte', 'start_interval'),
        ('timestamp__lte', 'end_interval'),
    )

    def get_queryset(self):
        if self.current_car:
            self.queryset = TaxiTrip.objects.filter(car=self.current_car).all()
        return super().get_queryset()


class ViewCarAccount(UniversalFilterListView):
    model = Car
    template_name = 'carmanagment/acccount_list.html'
    paginate_by = 20
    filtering = (
        ('name',),
    )


class ViewCarInvestmentAccount(ViewCarAccount):
    model = Car
    template_name = 'carmanagment/inest_list.html'
    paginate_by = 20
    filtering = (
        ('name',),
    )


class ViewInvestorAccount(ViewCarAccount):
    model = Investor


class ViewDriverAccount(ViewCarAccount):
    model = Driver


class ViewCounterpartAccount(ViewCarAccount):
    model = Counterpart


class ViewTaxiOperatorAccount(ViewCarAccount):
    model = TaxiOperator


class ViewCarExpenses(UniversalFilterListView, ByCarView):
    model = Expenses
    template_name = 'carmanagment/cars_expenses_list.html'
    paginate_by = 20
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


class OperationsView(UniversalFilterListView):
    model = AccountTransaction
    template_name = 'carmanagment/operation_list.html'
    paginate_by = 20
    filtering = (
        ('account__name__icontains', 'name'),
        ('transaction__transactionTime__gte', 'start_interval'),
        ('transaction__transactionTime__lte', 'end_interval'),
    )


class TransactionView(UniversalFilterListView):
    model = Transaction
    template_name = 'carmanagment/transaction_list.html'
    paginate_by = 20
    filtering = (
        ('transactionTime__gte', 'start_interval'),
        ('transactionTime__lte', 'end_interval'),
    )


class ViewTripsNew(UniversalFilterListView):
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


class ViewTripsNew2(UniversalFilterListView):
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