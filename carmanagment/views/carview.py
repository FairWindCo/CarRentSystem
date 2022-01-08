from datetime import timedelta

from django import forms
from django.shortcuts import render
from django.utils.timezone import now
from django.views.generic import ListView

from carmanagment.models import Car, TripStatistics, Expenses
from carmanagment.views.global_menu import GlobalMainMenu
from django_helpers.django_request_processor import UniversalFilterListView


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


class CarReportForm(forms.Form):
    start_date = forms.DateField(label='Дата начала периода', widget=forms.DateInput(format='%Y-%m-%d'),
                                 initial=(now() - timedelta(days=7)).date().strftime('%Y-%m-%d'))
    end_date = forms.DateField(label='Дата конца периода', widget=forms.DateInput(format='%Y-%m-%d'),
                               initial=(now()).date().strftime('%Y-%m-%d'))
    car = forms.ModelChoiceField(label='Машина', queryset=Car.objects.all(),
                                 widget=forms.Select(attrs={'class': 'form-control round'}))


def day_usage_report(form, rent=False):
    start_date = form.cleaned_data['end_date']
    end_date = form.cleaned_data['start_date']
    car = form.cleaned_data['car']
    return form_day_usage_report(start_date, end_date, car, rent)


def form_empty_data():
    return {'total': {
        'amount': 0,
        'fuel': 0,
        'trip': 0,
        'mileage': 0,
        'car_amount': 0,
        'driver_amount': 0,
        'payer_amount': 0,
        'expense_amount': 0,
        'total_sum': 0,
        'full_total_payer_amount': 0,
        'total_bank': 0,
        'firm_rent': 0,
        'cash': 0
    },
        'object_list': []}


def form_day_usage_report(start_date, end_date, car, rent=False):
    total_rent, total_fuel, total_trip, expense_amount = 0, 0, 0, 0
    total_millage, total_car_amount, total_driver, total_payer_amount = 0, 0, 0, 0
    full_total_payer_amount = 0
    total_bank = 0
    firm_rent = 0
    cash = 0

    cars_trips_stat = TripStatistics.objects.filter(
        car_in_rent=rent,
        stat_date__lte=start_date,
        stat_date__gte=end_date,
        car=car).all()
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
        cash += trip_stat.cash
    # print(rent, cars_trips_stat)
    return {'total': {
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
        'total_bank': total_bank,
        'firm_rent': firm_rent,
        'cash': cash
    }, 'object_list': cars_trips_stat}


def car_usage_report(request):
    context = GlobalMainMenu.form_menu_context(request)
    expenses = []
    expense_amount = 0
    trip_stat = form_empty_data()
    rent_trip_stat = form_empty_data()
    if request.method == 'POST':
        form = CarReportForm(request.POST)
        if form.is_valid():
            expenses = Expenses.objects.filter(account=form.cleaned_data['car'],
                                               date_mark__lte=form.cleaned_data['end_date'],
                                               date_mark__gte=form.cleaned_data['start_date']
                                               ).all()
            expense_amount = sum(expense.amount for expense in expenses)
            trip_stat = day_usage_report(form, False)
            rent_trip_stat = day_usage_report(form, True)
    else:
        form = CarReportForm()

    context['form'] = form
    context['trip_stat'] = trip_stat
    context['rent_trip_stat'] = rent_trip_stat
    context['expenses'] = expenses
    context['expense_amount'] = expense_amount
    return render(request, 'carmanagment/car_report.html', context)
