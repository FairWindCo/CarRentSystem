import bs4
import requests


def convert_string_html_to_float(string_value) -> float:
    string_val = str(string_value).strip()
    try:
        return float(string_val)
    except ValueError:
        return 0


def parse_html(html_data):
    fuel_price = {
        'disel': 0,
        'gas': 0,
        'a95': 0,
        'a92': 0
    }
    result = False
    soap = bs4.BeautifulSoup(html_data, features="html.parser")
    fuel_table = soap.find('div', class_='biz-listoil-page')
    if fuel_table:
        columns = fuel_table.find_all('td')
        if columns:
            fuel_price['a95'] = convert_string_html_to_float(columns[1].string)
            fuel_price['a92'] = convert_string_html_to_float(columns[5].string)
            fuel_price['disel'] = convert_string_html_to_float(columns[9].string)
            fuel_price['gas'] = convert_string_html_to_float(columns[13].string)
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
    response = requests.get('https://biz.liga.net/tek/oil')
    if response.status_code == 200:
        result, fuel_price = parse_html(response.text)
    return result, fuel_price


if __name__ == '__main__':
    print(get_fuel_price())
