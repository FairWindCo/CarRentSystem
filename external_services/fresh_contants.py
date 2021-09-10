import os
import sys

import django


def get_special_fuel_help_text(field_id='id_gas_price'):
    from constance import config
    FUELS = {
        'FUEL_A92': 'A92',
        'FUEL_A95': 'A95',
        'FUEL_DISEL': 'Дизель',
        'FUEL_GAS': 'Газ',
    }
    fuels_strings = "".join([f'<a href="#" onclick="{field_id}.value= {getattr(config, fuel_code)}; return false;">{name}: {getattr(config, fuel_code)} грн/л</a><br>'
                     for fuel_code, name in FUELS.items()])
    return fuels_strings



def refresh_contants():
    from external_services.currency_request import get_currency
    from external_services.fuel_price_request import get_fuel_price
    from constance.management.commands.constance import _set_constance_value

    result, fuel_data = get_fuel_price()
    if result:
        for name, value in fuel_data.items():
            field_name = f'fuel_{name}'.upper()
            _set_constance_value(field_name, value)

    result, currency_data = get_currency()
    if result:
        _set_constance_value('USD_CURRENCY', currency_data['$'])


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))

    os.environ['DJANGO_SETTINGS_MODULE'] = 'CarRentSystem.settings'

    django.setup()
    refresh_contants()
    get_special_fuel_help_text()
