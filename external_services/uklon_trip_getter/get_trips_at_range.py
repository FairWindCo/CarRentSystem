import datetime
from .uklon_service import LOCAL_TIMEZONE


def get_uklon_taxi_trip(fuel_prices,
                        last_day_rides: datetime.date = datetime.date.today() - datetime.timedelta(days=1),
                        day_count=1,
                        cache_path=None,
                        use_silenuim=False):
    from CarRentSystem import settings
    from carmanagment.models import CarsInOperator
    from external_services.uklon_trip_getter.uklon_service import UklonTaxiService
    from carmanagment.models import get_fuel_price_for_type
    from carmanagment.models import TaxiTrip
    user_name = settings.UKLON_USER
    user_pass = settings.UKLON_PASS

    # print(user_name, user_pass)
    uklon = UklonTaxiService(user_name, user_pass)
    if uklon.connect(selenium=use_silenuim):
        if uklon.get_my_info():
            stat_date = last_day_rides - datetime.timedelta(days=day_count)
            processed_rides = 0
            total_rides = 0
            for i in range(day_count):
                rides = uklon.get_day_rides(stat_date, cache_path=cache_path)
                uklon_cars = CarsInOperator.objects
                for ride in rides:
                    if ride['status'] == 'completed':
                        uklon_car_id = ride['vehicle_id']
                        try:
                            taxi_car_driver = uklon_cars.get(car_uid=uklon_car_id)
                            car = taxi_car_driver.car
                            driver = taxi_car_driver.driver
                            operator = taxi_car_driver.operator
                            cash = ride['cash_many_info']
                            gas_price = get_fuel_price_for_type(car.model.type_class, fuel_prices)
                            start_time = datetime.datetime.fromtimestamp(ride['pickup_time']).astimezone(LOCAL_TIMEZONE)
                            TaxiTrip.manual_create_taxi_trip(car, driver, start_time, operator, ride['distance'],
                                                             ride['cost'], gas_price, cash, '', None)
                            processed_rides += 1
                        except CarsInOperator.DoesNotExist:
                            continue
                total_rides += len(rides)
                stat_date += datetime.timedelta(days=1)
            uklon.logout()
            return processed_rides, total_rides
    return 0, 0
