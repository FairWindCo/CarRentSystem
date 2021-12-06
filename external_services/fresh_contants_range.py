import datetime
import os
import sys

import django
from django.utils import timezone


def get_special_fuel_help_text(field_id='id_gas_price'):
    from constance import config
    FUELS = {
        'FUEL_A92': 'A92',
        'FUEL_A95': 'A95',
        'FUEL_DISEL': 'Дизель',
        'FUEL_GAS': 'Газ',
    }
    fuels_strings = "".join([
        f'<a href="#" onclick="{field_id}.value= {round(getattr(config, fuel_code), 2)}; return false;">{name}: {round(getattr(config, fuel_code), 2)} грн/л</a><br>'
        for fuel_code, name in FUELS.items()])
    return fuels_strings


def get_uklon_taxi_trip(fuel_prices, use_silenuim=False, day_count=9):
    from CarRentSystem import settings
    from carmanagment.models import CarsInOperator
    from external_services.uklon_service import UklonTaxiService
    from carmanagment.models import get_fuel_price_for_type
    from carmanagment.models import TaxiTrip
    user_name = settings.UKLON_USER
    user_pass = settings.UKLON_PASS

    # print(user_name, user_pass)
    uklon = UklonTaxiService(user_name, user_pass)
    if uklon.connect(selenium=use_silenuim):
        if uklon.get_my_info():
            current_date = timezone.now()
            yesterday = current_date - datetime.timedelta(days=1)
            stat_date = yesterday - datetime.timedelta(days=day_count)
            processed_rides = 0
            total_rides = 0
            for i in range(day_count):
                print(stat_date)
                rides = uklon.get_day_rides(stat_date)
                uklon_cars = CarsInOperator.objects
                for ride in rides:
                    if ride['status'] == 'completed':
                        uklon_car_id = ride['vehicle_id']
                        try:
                            taxi_car_driver = uklon_cars.get(car_uid=uklon_car_id)
                            car = taxi_car_driver.car
                            driver = taxi_car_driver.driver
                            operator = taxi_car_driver.operator
                            cash = ride['payments']['fee_type'] == 'cash'
                            gas_price = get_fuel_price_for_type(car.model.type_class, fuel_prices)
                            start_time = datetime.datetime.fromtimestamp(ride['pickup_time'])
                            TaxiTrip.manual_create_taxi_trip(car, driver, start_time, operator, ride['distance'],
                                                             ride['cost'], gas_price, cash, '', operator.cash_box)
                            processed_rides += 1
                        except CarsInOperator.DoesNotExist:
                            continue
                total_rides += len(rides)
                stat_date += datetime.timedelta(days=1)
            uklon.logout()
            return processed_rides, total_rides
    return 0, 0


def refresh_contants():
    from external_services.currency_request import get_currency
    from external_services.fuel_price_request import get_fuel_price
    from constance.management.commands.constance import _set_constance_value

    result, fuel_data = get_fuel_price()
    if result:
        for name, value in fuel_data.items():
            field_name = f'fuel_{name}'.upper()
            _set_constance_value(field_name, value)
        print(get_uklon_taxi_trip(fuel_data))

    result, currency_data = get_currency()
    if result:
        _set_constance_value('USD_CURRENCY', currency_data['$'])


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.abspath(BASE_DIR))
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))

    os.environ['DJANGO_SETTINGS_MODULE'] = 'CarRentSystem.settings'

    django.setup()
    refresh_contants()
    get_special_fuel_help_text()
