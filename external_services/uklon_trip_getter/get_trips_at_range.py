import datetime

from .uklon_service import LOCAL_TIMEZONE


def process_uklon_trip(ride, operator, fuel_prices):
    from trips.models.taxi import TaxiTrip

    if ride['status'] == 'completed':
        uklon_car_id = ride['driver_id']

        start_time = datetime.datetime.fromtimestamp(ride['pickup_time']).astimezone(LOCAL_TIMEZONE)
        res = TaxiTrip.auto_create_trip(start_time, operator, uklon_car_id,
                                        ride['distance'],
                                        ride['cost'],
                                        fuel_prices,
                                        ride['cash_many_info'])
        return res
    return False


def get_uklon_taxi_trip(fuel_prices,
                        last_day_rides: datetime.date = datetime.date.today() - datetime.timedelta(days=1),
                        day_count=1,
                        cache_path=None,
                        use_silenuim=False,
                        create_summary=True):
    from car_rent.models import CarSchedule
    from CarRentSystem import settings
    from external_services.uklon_trip_getter.uklon_service import UklonTaxiService
    from car_management.models import get_fuel_price_for_type
    from car_rent.models import CarsInOperator, TaxiOperator
    from trips.models.taxi import TripStatistics

    user_name = settings.UKLON_USER
    user_pass = settings.UKLON_PASS
    operator = TaxiOperator.objects.get(name='УКЛОН')

    # print(user_name, user_pass)
    uklon = UklonTaxiService(user_name, user_pass)
    if uklon.connect(selenium=use_silenuim):
        if uklon.get_my_info():
            uklon.get_partner_drivers_and_cars()
            for signal, driver in uklon.drivers.items():
                try:
                    taxi = CarsInOperator.objects.get(signal=signal, operator=operator)
                    if not taxi.car_uid:
                        taxi.car_uid = driver['uid']
                        taxi.save()
                except CarsInOperator.DoesNotExist:
                    pass
            stat_date = last_day_rides - datetime.timedelta(days=day_count)
            processed_rides = 0
            total_rides = 0
            for i in range(day_count):
                print('STAT DAY', stat_date)
                rides = uklon.get_day_rides(stat_date, cache_path=cache_path)
                for ride in rides:
                    if process_uklon_trip(ride, operator, fuel_prices):
                        processed_rides += 1
                if create_summary:
                    summaries = uklon.get_uklon_summary_report(stat_date)
                    for summary in summaries:
                        try:
                            start = datetime.datetime.combine(stat_date, datetime.time.min)
                            taxi_car_driver = CarSchedule.find_schedule_info(summary['driver_id'], start, operator)
                            if taxi_car_driver is None:
                                continue
                            car = taxi_car_driver.car
                            driver = taxi_car_driver.driver
                            terms = taxi_car_driver.term
                            gas_price = get_fuel_price_for_type(car.model.type_class, fuel_prices)
                            print(summary['trip_count'], summary['car_plate'], stat_date)
                            TripStatistics.manual_create_summary_paid(car, driver, stat_date, operator, terms,
                                                                      summary['millage'],
                                                                      summary['total'],
                                                                      gas_price,
                                                                      summary['cash'],
                                                                      summary['trip_count'],
                                                                      comment=f'Доход от машины {car.name} за {stat_date}',
                                                                      many_cash_box=None,
                                                                      car_in_taxi=taxi_car_driver.work_in_taxi,
                                                                      transaction_type=taxi_car_driver.paid_type
                                                                      )
                        except CarsInOperator.DoesNotExist:
                            pass
                total_rides += len(rides)
                stat_date += datetime.timedelta(days=1)
            uklon.logout()
            return processed_rides, total_rides
    return 0, 0
