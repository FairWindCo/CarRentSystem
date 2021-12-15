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