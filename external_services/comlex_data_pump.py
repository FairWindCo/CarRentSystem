import datetime

from external_services.argument_parser import parse_args
from external_services.django_common.django_native_execute import execute_code_in_django
from uklon_trip_getter.get_trips_at_range import get_uklon_taxi_trip
from fresh_statistics import fresh_statistics_on_range


def uklon_data_pump(start_date: datetime.date = datetime.date.today() - datetime.timedelta(days=1),
                    days_count=7,
                    cache_path=None):
    from external_services.currency_request import get_currency
    from external_services.fuel_statisitics.minfin_server import get_fuel_price
    from constance.management.commands.constance import _set_constance_value

    result, currency_data = get_currency()
    if result:
        _set_constance_value('USD_CURRENCY', currency_data['$'])

    result, fuel_data = get_fuel_price()
    if result:
        for name, value in fuel_data.items():
            field_name = f'fuel_{name}'.upper()
            _set_constance_value(field_name, value)
        proccessed, total = get_uklon_taxi_trip(fuel_data, start_date, days_count, cache_path=cache_path)
        print(f'import {proccessed} trips from {total}')
        if proccessed > 0:
            fresh_statistics_on_range(start_date, days_count)


if __name__ == '__main__':
    start_date, days, path = parse_args('Get car data from Uklon')
    execute_code_in_django(lambda: uklon_data_pump(start_date=start_date, days_count=days, cache_path=path))
