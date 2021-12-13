import datetime

from django.db import IntegrityError
from django.utils import timezone

from carmanagment.models import Car, Expenses, TaxiTrip, TripStatistics


def get_sum(dict_obj, name):
    value = dict_obj.get(name, None)
    return value if value is not None else 0


class Statistics:
    LOCAL_TIMEZONE = datetime.datetime.now(timezone.utc).astimezone().tzinfo

    @staticmethod
    def create_car_statistics(car: Car, statistics_date: datetime.date):
        from django.db.models import Sum, Count
        if statistics_date is None:
            statistics_date = timezone.now().date()

        statistics_start_date = datetime.datetime.combine(statistics_date,
                                                                         datetime.datetime.min.time(),
                                                                         Statistics.LOCAL_TIMEZONE)
        statistics_end_date = statistics_start_date + datetime.timedelta(days=1)
        print(statistics_start_date)
        expenses_sum = Expenses.objects.filter(account=car,
                                               date_mark__lte=statistics_end_date,
                                               date_mark__gte=statistics_start_date).aggregate(Sum('amount'))
        cash_sum = TaxiTrip.objects.filter(car=car, is_rent=False,
                                               timestamp__lte=statistics_end_date,
                                               timestamp__gte=statistics_start_date).aggregate(Sum('many_in_cash'))
        trip_sum = TaxiTrip.objects.filter(car=car, is_rent=False,
                                           timestamp__lte=statistics_end_date,
                                           timestamp__gte=statistics_start_date). \
            aggregate(Sum('mileage'),
                      Sum('fuel'),
                      Sum('amount'),
                      Sum('car_amount'),
                      Sum('payer_amount'),
                      Sum('driver_amount'),
                      Sum('bank_amount'),
                      Sum('firm_rent'),
                      Sum('total_payer_amount'),
                      Count('pk')
                      )
        try:
            TripStatistics(car=car,
                           stat_date=statistics_start_date.date(),
                           mileage=get_sum(trip_sum, 'mileage__sum'),
                           fuel=get_sum(trip_sum, 'fuel__sum'),
                           amount=get_sum(trip_sum, 'amount__sum'),
                           car_amount=get_sum(trip_sum, 'car_amount__sum'),
                           driver_amount=get_sum(trip_sum, 'driver_amount__sum'),
                           payer_amount=get_sum(trip_sum, 'payer_amount__sum'),
                           expanse_amount=get_sum(expenses_sum, 'amount__sum'),
                           total_payer_amount=get_sum(trip_sum, 'total_payer_amount__sum'),
                           total_firm_rent=get_sum(trip_sum, 'firm_rent__sum'),
                           total_bank_rent=get_sum(trip_sum, 'bank_amount__sum'),
                           trip_count=get_sum(trip_sum, 'pk__count'),
                           cash=get_sum(cash_sum, 'many_in_cash__sum')
                           ).save()
        except IntegrityError as e:
            stat = TripStatistics.objects.get(car=car, stat_date=statistics_start_date.date())
            stat.mileage = get_sum(trip_sum, 'mileage__sum')
            stat.fuel = get_sum(trip_sum, 'fuel__sum')
            stat.amount = get_sum(trip_sum, 'amount__sum')
            stat.car_amount = get_sum(trip_sum, 'car_amount__sum')
            stat.driver_amount = get_sum(trip_sum, 'driver_amount__sum')
            stat.payer_amount = get_sum(trip_sum, 'payer_amount__sum')
            stat.expanse_amount = get_sum(expenses_sum, 'amount__sum')
            stat.total_payer_amount = get_sum(trip_sum, 'total_payer_amount__sum')
            stat.total_firm_rent = get_sum(trip_sum, 'firm_rent__sum')
            stat.total_bank_rent = get_sum(trip_sum, 'bank_amount__sum')
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