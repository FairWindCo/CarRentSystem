import bs4
import requests

from external_services.fuel_statisitics.django_fuel_config import convert_string_html_to_float, \
    form_simple_empty_fuel_price, AvarageDict


def parse_avtomania_html(html_data, only_azs=None):
    fuel_price = form_simple_empty_fuel_price()

    def get_fuel_from_record(row):
        fuel_price = form_simple_empty_fuel_price()
        columns = row.find_all('td')
        name = columns[1].string
        fuel_price['a98'] = convert_string_html_to_float(columns[2].string)
        fuel_price['a95+'] = convert_string_html_to_float(columns[3].string)
        fuel_price['a95'] = convert_string_html_to_float(columns[4].string)
        fuel_price['a92'] = convert_string_html_to_float(columns[5].string)
        fuel_price['disel'] = convert_string_html_to_float(columns[7].string)
        fuel_price['disel+'] = convert_string_html_to_float(columns[8].string)
        fuel_price['gas'] = convert_string_html_to_float(columns[9].string)
        return fuel_price, name

    result = False
    soap = bs4.BeautifulSoup(html_data, features="html.parser")
    fuel_table = soap.find('div', class_='prices-for-kiev')
    if fuel_table:
        rows = fuel_table.find_all('tr', class_='benz_line')
        if only_azs and isinstance(only_azs, int):
            if only_azs < len(rows):
                fuel_price, _ = get_fuel_from_record(rows[only_azs])
                return True, fuel_price
            else:
                return False, fuel_price
        else:
            avarage = AvarageDict()
            for row in rows:
                fuel_price_azs, name = get_fuel_from_record(row)
                if only_azs is None:
                    avarage.update(fuel_price_azs)
                elif name == only_azs:
                    return True, fuel_price_azs
            avg_fuel_price = avarage.get_average()
            if avg_fuel_price:
                fuel_price = avg_fuel_price
                result = True
    return result, fuel_price


def get_fuel_price_avtomaniya():
    fuel_price = {
        'disel': 0,
        'gas': 0,
        'a95': 0,
        'a92': 0
    }
    result = False
    response = requests.get('https://avtomaniya.com/benzin')
    if response.status_code == 200:
        result, fuel_price = parse_avtomania_html(response.text)
    return result, fuel_price