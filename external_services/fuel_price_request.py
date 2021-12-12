import bs4
import requests


def convert_string_html_to_float(string_value) -> float:
    string_val = str(string_value).strip()
    try:
        string_val = string_val.replace(',', '.')
        return float(string_val)
    except ValueError:
        return 0


def form_simple_empty_fuel_price():
    return {
        'disel': 0.0,
        'gas': 0.0,
        'a95': 0.0,
        'a92': 0.0
    }


def parse_liga_html(html_data):
    fuel_price = form_simple_empty_fuel_price()
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


class AvarageDict:
    def __init__(self, default_value=0, ignore_old_values=True):
        self.value_dict = dict()
        self.count_dict = dict()
        self.ignore_old_values = ignore_old_values
        self.default_value = default_value

    def update(self, new_values_dict: dict):
        for name, value in new_values_dict.items():
            self.update_value(name, value)

    def update_value(self, key, value):
        if self.ignore_old_values and value == self.default_value:
            return
        count = self.count_dict.get(key, 0)
        old_value = self.value_dict.get(key, self.default_value)
        self.value_dict[key] = old_value + value
        self.count_dict[key] = count + 1

    def get_average(self):
        result = dict()

        for name, value in self.value_dict.items():
            result[name] = value / self.count_dict[name]
        return result


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


def get_liga_fuel_price():
    fuel_price = {
        'disel': 0,
        'gas': 0,
        'a95': 0,
        'a92': 0
    }
    result = False
    response = requests.get('https://biz.liga.net/tek/oil')
    if response.status_code == 200:
        result, fuel_price = parse_liga_html(response.text)
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


if __name__ == '__main__':
    print(get_fuel_price())
