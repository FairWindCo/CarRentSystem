import datetime

from django.db import IntegrityError
from django.utils import timezone

from carmanagment.models import Car, Expenses, TaxiTrip, TripStatistics


def get_sum(dict_obj, name):
    value = dict_obj.get(name, None)
    return value if value is not None else 0


class Statistics:
    @staticmethod
    def create_car_statistics(car: Car, statistics_date: datetime.date):
        from django.db.models import Sum, Count
        if statistics_date is None:
            statistics_date = timezone.now().date()
        statistics_start_date: datetime.date = statistics_date
        statistics_end_date: datetime.date = statistics_start_date + datetime.timedelta(days=1)
        expenses_sum = Expenses.objects.filter(account=car,
                                               date_mark__lte=statistics_end_date,
                                               date_mark__gte=statistics_start_date).aggregate(Sum('amount'))
        trip_sum = TaxiTrip.objects.filter(car=car,
                                           timestamp__lte=statistics_end_date,
                                           timestamp__gte=statistics_start_date). \
            aggregate(Sum('mileage'),
                      Sum('fuel'),
                      Sum('amount'),
                      Sum('car_amount'),
                      Sum('payer_amount'),
                      Sum('driver_amount'),
                      Count('pk')
                      )
        try:
            TripStatistics(car=car,
                           stat_date=statistics_start_date,
                           mileage=get_sum(trip_sum, 'mileage__sum'),
                           fuel=get_sum(trip_sum, 'fuel__sum'),
                           amount=get_sum(trip_sum, 'amount__sum'),
                           car_amount=get_sum(trip_sum, 'car_amount__sum'),
                           driver_amount=get_sum(trip_sum, 'driver_amount__sum'),
                           payer_amount=get_sum(trip_sum, 'payer_amount__sum'),
                           expanse_amount=get_sum(expenses_sum, 'amount__sum'),
                           trip_count=get_sum(trip_sum, 'pk__count'),
                           ).save()
        except IntegrityError as e:
            stat = TripStatistics.objects.get(car=car, stat_date=statistics_start_date)
            stat.mileage = get_sum(trip_sum, 'mileage__sum')
            stat.fuel = get_sum(trip_sum, 'fuel__sum')
            stat.amount = get_sum(trip_sum, 'amount__sum')
            stat.car_amount = get_sum(trip_sum, 'car_amount__sum')
            stat.driver_amount = get_sum(trip_sum, 'driver_amount__sum')
            stat.payer_amount = get_sum(trip_sum, 'payer_amount__sum')
            stat.expanse_amount = get_sum(expenses_sum, 'amount__sum')
            stat.trip_count = get_sum(trip_sum, 'pk__count')
            stat.save()

    @staticmethod
    def create_statistics(statistics_date: datetime.date = None):
        if statistics_date is None:
            statistics_date = timezone.now()

        cars = Car.objects.all()

        for car in cars:
            Statistics.create_car_statistics(car, statistics_date)

    @staticmethod
    def get_last_statistics():
        cars = Car.objects.all()
        return {car.name: list(car.tripstatistics_set.order_by('-stat_date').all()[:7]) for car in cars}