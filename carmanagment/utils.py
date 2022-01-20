def get_sum(dict_obj, name):
    value = dict_obj.get(name, None)
    return value if value is not None else 0