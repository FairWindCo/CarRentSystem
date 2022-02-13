import datetime

from django.db import IntegrityError
from django.utils import timezone

from car_management.models import Car, Expenses, WialonDayStat, ExpensesTypes
from car_rent.models.branding import BrandingAmount
from car_rent.models import CarSchedule
from trip_stat.models.statistics import CarSummaryStatistics
from car_management.utils import get_sum
from trips.models.taxi import TaxiTrip, TripStatistics


class Statistics:
    LOCAL_TIMEZONE = datetime.datetime.now(timezone.utc).astimezone().tzinfo

    @staticmethod
    def create_car_statistics(car: Car, statistics_date: datetime.date, rent_car=False):
        from django.db.models import Sum, Count
        if statistics_date is None:
            statistics_date = timezone.now().date()

        statistics_start_date = datetime.datetime.combine(statistics_date,
                                                          datetime.datetime.min.time(),
                                                          Statistics.LOCAL_TIMEZONE)
        statistics_end_date = statistics_start_date + datetime.timedelta(days=1)
        # print(statistics_start_date)
        trip_sum = TaxiTrip.objects.filter(car=car, is_rent=rent_car,
                                           timestamp__lte=statistics_end_date,
                                           timestamp__gte=statistics_start_date). \
            aggregate(Sum('mileage'),
                      Sum('fuel'),
                      Sum('amount'),
                      Sum('many_in_cash'),

                      Sum('payer_amount'),
                      Sum('driver_amount'),
                      Sum('bank_amount'),
                      Sum('operating_services'),
                      Sum('investor_rent'),

                      Count('pk')
                      )
        trip_count = get_sum(trip_sum, 'pk__count')
        if trip_count < 1:
            return

        try:
            trip_stat = TripStatistics(car=car,
                                       stat_date=statistics_start_date.date(),
                                       car_in_rent=rent_car
                                       )
            trip_stat.save()
        except IntegrityError as _:
            trip_stat = TripStatistics.objects.get(car=car, stat_date=statistics_start_date.date(),
                                                   car_in_rent=rent_car)

        trip_stat.mileage = get_sum(trip_sum, 'mileage__sum')
        trip_stat.trip_count = trip_count
        trip_stat.fuel = get_sum(trip_sum, 'fuel__sum')
        trip_stat.amount = get_sum(trip_sum, 'amount__sum')
        trip_stat.cash = get_sum(trip_sum, 'many_in_cash__sum')

        trip_stat.investor_amount = get_sum(trip_sum, 'investor_rent__sum')
        trip_stat.driver_amount = get_sum(trip_sum, 'driver_amount__sum')
        trip_stat.payer_amount = get_sum(trip_sum, 'payer_amount__sum')
        trip_stat.operating_services = get_sum(trip_sum, 'operating_services__sum')
        trip_stat.bank_amount = get_sum(trip_sum, 'bank_amount__sum')
        trip_stat.save()
        return trip_stat

    @staticmethod
    def create_car_summary_statistics(trip_stat):
        from django.db.models import Sum
        statistics_date = trip_stat.stat_date
        car = trip_stat.car
        statistics_start_date = datetime.datetime.combine(statistics_date,
                                                          datetime.datetime.min.time(),
                                                          Statistics.LOCAL_TIMEZONE)
        statistics_end_date = statistics_start_date + datetime.timedelta(days=1)

        # expenses_sum = Expenses.objects.filter(account=car,
        #                                        date_mark__lte=statistics_end_date,
        #                                        date_mark__gte=statistics_start_date).aggregate(Sum('amount'))
        #
        # capital_sum = Expenses.objects.filter(account=car,
        #                                       expenseType=ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE,
        #                                       date_mark__lte=statistics_end_date,
        #                                       date_mark__gte=statistics_start_date).aggregate(Sum('amount'))

        expenses_sum = Expenses.objects.values('expenseType'). \
            annotate(amount=Sum('amount'), franchise=Sum('franchise')). \
            filter(account=car,
                   date_mark__lte=statistics_end_date,
                   date_mark__gte=statistics_start_date)
        try:
            expense = get_sum(expenses_sum.get(expenseType=ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE),
                              'amount')
        except Expenses.DoesNotExist:
            expense = 0
        try:
            capital = expenses_sum.get(expenseType=ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE)
            capital_expense = get_sum(capital, 'amount')
            franchise = get_sum(capital, 'franchise')
        except Expenses.DoesNotExist:
            capital_expense = 0
            franchise = 0
        try:
            car_summary = CarSummaryStatistics(car=car, stat_date=statistics_date, stat_interval=86400)
            car_summary.save()
        except IntegrityError:
            car_summary = CarSummaryStatistics.objects.get(car=car, stat_date=statistics_date, stat_interval=86400)
        # car_summary.rent_amount
        car_summary.taxi_trip_count = trip_stat.trip_count
        car_summary.taxi_amount = trip_stat.clean_car_amount
        car_summary.investor_amount = trip_stat.investor_amount
        car_summary.driver_amount = trip_stat.driver_amount
        car_summary.taxi_mileage = trip_stat.mileage
        car_summary.expense = expense + franchise
        car_summary.capital_expense = capital_expense
        car_summary.operate = trip_stat.operating_services
        try:
            branding = BrandingAmount.objects.get(car=car, stat_date=statistics_date)
            car_summary.branding_amount = branding.amount
            car_summary.investor_amount += branding.investor_amount
            car_summary.operate += branding.operate
        except BrandingAmount.DoesNotExist:
            pass
        try:
            wialon = WialonDayStat.objects.get(car=car, stat_date=statistics_date, stat_interval=86400)
            car_summary.gps_mileage = wialon.mileage
        except WialonDayStat.DoesNotExist:
            pass
        rent = CarSchedule.object_date_in_interval(car=car, date_time=statistics_date)
        if rent and not rent.work_in_taxi:
            car_summary.rent_amount = rent.rent_price
        car_summary.save()

    @staticmethod
    def create_statistics(statistics_date: datetime.date = None):
        if statistics_date is None:
            statistics_date = timezone.now()

        cars = Car.objects.all()

        for car in cars:
            # подсчет статистики для машины в такси
            taxi_trip = Statistics.create_car_statistics(car, statistics_date, False)
            # подсчет статистики для машины в аренде
            rent_trip = Statistics.create_car_statistics(car, statistics_date, True)
            if taxi_trip and taxi_trip.amount > 0:
                Statistics.create_car_summary_statistics(taxi_trip)
            elif rent_trip:
                Statistics.create_car_summary_statistics(rent_trip)

    @staticmethod
    def get_last_statistics():
        cars = Car.objects.all()
        return {car.name: list(car.tripstatistics_set.order_by('-stat_date').all()[:7]) for car in cars}