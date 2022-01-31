import datetime

from wialon_reports.WialonReporter import date_to_correct_time
from .uklon_service import LOCAL_TIMEZONE


def get_uklon_taxi_trip(fuel_prices,
                        last_day_rides: datetime.date = datetime.date.today() - datetime.timedelta(days=1),
                        day_count=1,
                        cache_path=None,
                        use_silenuim=False,
                        summary_paid=True, create_summary=True):
    from CarRentSystem import settings
    from car_management.models import CarsInOperator
    from external_services.uklon_trip_getter.uklon_service import UklonTaxiService
    from car_management.models import get_fuel_price_for_type
    from car_management.models import TaxiTrip, TripStatistics
    user_name = settings.UKLON_USER
    user_pass = settings.UKLON_PASS

    # print(user_name, user_pass)
    uklon = UklonTaxiService(user_name, user_pass)
    if uklon.connect(selenium=use_silenuim):
        if uklon.get_my_info():
            uklon.get_partner_drivers_and_cars()
            for signal, driver in uklon.drivers.items():
                try:
                    taxi = CarsInOperator.objects.get(signal=signal)
                    if not taxi.car_uid:
                        taxi.car_uid = driver['uid']
                        taxi.save()
                except CarsInOperator.DoesNotExist:
                    pass
            stat_date = last_day_rides - datetime.timedelta(days=day_count)
            processed_rides = 0
            skip_rides = 0
            total_rides = 0
            for i in range(day_count):
                print('STAT DAY', stat_date)
                rides = uklon.get_day_rides(stat_date, cache_path=cache_path)
                uklon_cars = CarsInOperator.objects
                for ride in rides:
                    if ride['status'] == 'completed':
                        uklon_car_id = ride['driver_id']
                        try:
                            taxi_car_driver = uklon_cars.get(car_uid=uklon_car_id)
                            car = taxi_car_driver.car
                            driver = taxi_car_driver.driver
                            operator = taxi_car_driver.operator
                            cash = ride['cash_many_info']
                            gas_price = get_fuel_price_for_type(car.model.type_class, fuel_prices)
                            start_time = datetime.datetime.fromtimestamp(ride['pickup_time']).astimezone(LOCAL_TIMEZONE)
                            res = TaxiTrip.manual_create_taxi_trip(car, driver, start_time, operator, ride['distance'],
                                                                   ride['cost'], gas_price, cash, '', None,
                                                                   only_statistics=summary_paid)
                            if res:
                                processed_rides += 1
                            else:
                                skip_rides += 1
                        except CarsInOperator.DoesNotExist:
                            continue
                if create_summary:
                    summaries = uklon.get_uklon_summary_report(stat_date)
                    for summary in summaries:
                        try:
                            taxi_car_driver = uklon_cars.get(car_uid=summary['driver_id'])
                            car = taxi_car_driver.car
                            driver = taxi_car_driver.driver
                            operator = taxi_car_driver.operator
                            gas_price = get_fuel_price_for_type(car.model.type_class, fuel_prices)
                            print(summary['trip_count'], summary['car_plate'], stat_date)
                            TripStatistics.manual_create_summary_paid(car, driver, stat_date, operator,
                                                                      summary['millage'],
                                                                      summary['total'],
                                                                      gas_price,
                                                                      summary['cash'],
                                                                      summary['trip_count'],
                                                                      comment=f'Доход от машины {car.name} за {stat_date}',
                                                                      many_cash_box=None,
                                                                      only_statistics=False, )
                        except CarsInOperator.DoesNotExist:
                            pass
                total_rides += len(rides)
                stat_date += datetime.timedelta(days=1)
            uklon.logout()
            return processed_rides, total_rides, skip_rides
    return 0, 0
