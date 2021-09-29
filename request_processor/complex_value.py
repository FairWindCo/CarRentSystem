import json
from json import JSONDecodeError
from urllib.parse import unquote

from request_processor.value_converters_utility import TypeValueProcessor



from django.db.models import Manager
from typing import Iterable, Any


class ComplexTypeValue(TypeValueProcessor):
    string_name_separator = ','

    def __init__(self, name: str, default_value: Any = None, value: Any = None, raise_exception: bool = False):
        if not name:
            raise ValueError('name cannot be empty!')

        self.name = name
        self.default_value = default_value
        self.raise_exception = raise_exception
        if value is None:
            self.value = default_value
            self.real_value = False
        else:
            self.value = value
            self.real_value = True

    @classmethod
    def get_prototype(cls, value: Any, _first_level: bool = True):
        if isinstance(value, str):
            if value.find(ComplexTypeValue.string_name_separator) >= 0:
                names = value.split(ComplexTypeValue.string_name_separator)
                return [cls(name) for name in names]
            else:
                return cls(value)
        elif isinstance(value, dict):
            return cls(**value)
        elif isinstance(value, Iterable):
            if _first_level:
                return [cls.get_prototype(one_value, False) for one_value in value]
            else:
                return cls(*value)
        elif isinstance(value, cls):
            return value
        else:
            raise ValueError('name cannot be empty!')

    @staticmethod
    def get_field_value(obj: any, field_name: str, default_val: any = None, can_call_function=True):
        if obj and field_name:
            if ComplexTypeValue.is_dict(obj):
                return obj.get(field_name, default_val)
            elif ComplexTypeValue.is_not_string_sequence(obj) and field_name.isnumeric():
                index = int(field_name)
                return default_val if len(obj) <= index else obj[index]
            elif hasattr(obj, field_name):
                val = getattr(obj, field_name)
                if can_call_function and callable(val) and not isinstance(val, Manager):
                    val = val()
                return val
            else:
                return default_val
        else:
            return default_val

    @staticmethod
    def get_from_request(request, request_param_name: str, default_value: any = None, raise_exception: bool = False,
                         request_methods: Iterable[str] = ('GET', 'POST', 'body')) -> (Any, bool):
        if request is None:
            if raise_exception:
                raise ValueError('Request is None')
            else:
                return default_value, False
        if request_param_name:
            for method_name in request_methods:
                method = ComplexTypeValue.get_field_value(request, method_name, None)
                if method:
                    if isinstance(method, bytes):
                        try:
                            method_str = method.decode('utf-8')
                            method = json.loads(method_str)
                        except JSONDecodeError or UnicodeDecodeError:
                            if raise_exception:
                                raise ValueError(f'No field {request_param_name} in request')
                            else:
                                return default_value, False
                    if request_param_name in method:
                        value = method.get(request_param_name)
                        if method == 'GET':
                            value = unquote(value)
                        return value, True
                    elif not request_param_name.endswith('[]'):
                        list_param_name = f'{request_param_name}[]'
                        if list_param_name in method:
                            return method.getlist(list_param_name), True
            if raise_exception:
                raise ValueError(f'No field {request_param_name} in request')
            else:
                return default_value, False
        else:
            if raise_exception:
                raise ValueError('Request parameter name empty')
            else:
                return default_value, False

    def analyse_request(self, request, request_methods):
        self.value, self.real_value = self.get_from_request(request, self.name, self.default_value,
                                                            self.raise_exception, request_methods)
