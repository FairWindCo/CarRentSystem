import bs4
import requests

from external_services.fuel_statisitics.django_fuel_config import convert_string_html_to_float


def parse_html(html_data, default_value):
    result = False
    soap = bs4.BeautifulSoup(html_data, features="html.parser")
    div = soap.find('div', class_='mfm-grey-bg')
    if div:
        currency_table = div.find('table', class_='mfcur-table-lg-currency')
        if currency_table:
            columns = currency_table.find_all('td')
            if columns:
                default_value['$'] = convert_string_html_to_float(columns[2].span.contents[0])
                default_value['руб'] = convert_string_html_to_float(columns[10].span.contents[0])
                default_value['euro'] = convert_string_html_to_float(columns[6].span.contents[0])
                result = True
    return result, default_value


def get_currency():
    currency = {
        '$': 0,
        'руб': 0,
        'euro': 0
    }
    result = False
    response = requests.get('https://minfin.com.ua/ua/currency/')
    if response.status_code == 200:
        result, currency = parse_html(response.text, currency)
    return result, currency


if __name__ == '__main__':
    print(get_currency())
