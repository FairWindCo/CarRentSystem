import bs4
import requests

from external_services.fuel_statisitics.django_fuel_config import form_simple_empty_fuel_price, \
    convert_string_html_to_float, AvarageDict


def parse_minfin_html(html_data, only_azs=None):
    fuel_price = form_simple_empty_fuel_price()

    def get_fuel_from_record(row):
        fuel_price = form_simple_empty_fuel_price()
        columns = row.find_all('td')
        name = columns[0].string
        fuel_price['a95+'] = convert_string_html_to_float(columns[2].string)
        fuel_price['a95'] = convert_string_html_to_float(columns[3].string)
        fuel_price['a92'] = convert_string_html_to_float(columns[4].string)
        fuel_price['disel'] = convert_string_html_to_float(columns[5].string)
        fuel_price['gas'] = convert_string_html_to_float(columns[6].string)
        return fuel_price, name

    result = False
    soap = bs4.BeautifulSoup(html_data, features="html.parser")
    fuel_table = soap.find(id='tm-table')
    if fuel_table:
        rows = fuel_table.find_all('tr')
        avarage = AvarageDict()
        for row in rows[1:]:
            fuel_price_azs, name = get_fuel_from_record(row)
            avarage.update(fuel_price_azs)
        avg_fuel_price = avarage.get_average()
        if avg_fuel_price:
            fuel_price = avg_fuel_price
            result = True
    return result, fuel_price


def get_fuel_price():
    fuel_price = {
        'disel': 0,
        'gas': 0,
        'a95': 0,
        'a92': 0
    }
    result = False
    response = requests.get('https://index.minfin.com.ua/ua/markets/fuel/reg/kievskaya/')
    if response.status_code == 200:
        result, fuel_price = parse_minfin_html(response.text)
    return result, fuel_price

if __name__ == '__main__':
    print(get_fuel_price())