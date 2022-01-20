import datetime

from argument_parser import parse_args
from django_common.django_native_execute import execute_code_in_django
from external_services.wialon_trips.wialon_trip_service import get_wialon_trip
from uklon_trip_getter.get_trips_at_range import get_uklon_taxi_trip
from fresh_statistics import fresh_statistics_on_range


def uklon_data_pump(pamp_start_date: datetime.date = datetime.date.today() - datetime.timedelta(days=1),
                    days_count=7,
                    cache_path=None):
    from currency_request import get_currency
    from fuel_statisitics.minfin_server import get_fuel_price
    from constance.management.commands.constance import _set_constance_value

    result, currency_data = get_currency()
    if result:
        _set_constance_value('USD_CURRENCY', currency_data['$'])

    result, fuel_data = get_fuel_price()

    if result:
        for name, value in fuel_data.items():
            field_name = f'fuel_{name}'.upper()
            _set_constance_value(field_name, value)
        proccessed, total, skip = get_uklon_taxi_trip(fuel_data, pamp_start_date, days_count, cache_path=cache_path)
        print(f'import {proccessed} trips, skip {skip} from {total}')
        if proccessed > 0:
            fresh_statistics_on_range(pamp_start_date, days_count)
    get_wialon_trip(last_day=pamp_start_date, day_count=days_count, show_info=False, cache_path=cache_path)


if __name__ == '__main__':
    start_date, days, path = parse_args('Get car data from Uklon')
    execute_code_in_django(lambda: uklon_data_pump(start_date=start_date, days_count=days, cache_path=path))
