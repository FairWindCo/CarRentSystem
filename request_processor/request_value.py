import datetime
import json
from typing import Iterable, Any, Callable, Union
import pytz
from request_processor.complex_value import ComplexTypeValue


class RequestValue(ComplexTypeValue):

    def __init__(self, parameter_name: str,
                 default_value: Any = None,
                 input_converter: Union[str, Callable] = None,
                 raise_exception: bool = False,
                 request_methods: Iterable[str] = ('GET', 'POST', 'body')
                 ):
        super(RequestValue, self).__init__(parameter_name, default_value, raise_exception=raise_exception)
        self.request_methods = request_methods
        self.input_converter = input_converter

    def analyse_request(self, request, request_methods):
        value, self.real_value = self.get_from_request(request, self.name, self.default_value,
                                                       self.raise_exception, request_methods)
        self.value = RequestValue.convert_from_value(value, self.input_converter, self.default_value,
                                                     self.raise_exception)

    def get_value_from_request(self, request):
        self.analyse_request(request, self.request_methods)

    @staticmethod
    def convert_from_value(value, input_converter: Union[str, Callable], default_value, raise_exception, *arg, **kwarg):
        if not input_converter:
            return value
        elif isinstance(input_converter, Callable):
            return input_converter(value, *arg, **kwarg)
        elif isinstance(input_converter, str):
            if input_converter == 'any':
                return value
            elif input_converter == 'to_int':
                return int(value)
            elif input_converter == 'to_float':
                return float(value)
            elif input_converter == 'to_str':
                return str(value)
            elif input_converter == 'from_timestamp':
                return datetime.datetime.fromtimestamp(value)
            elif input_converter.startswith('timestamp_'):
                time_zone_name = input_converter[len('timestamp_'):]
                tz = pytz.timezone(time_zone_name)
                return datetime.datetime.fromtimestamp(value, tz)
            elif input_converter == 'to_json':
                return json.load(value)
            elif input_converter == 'from_json':
                return json.dumps(value)

        if raise_exception:
            raise ValueError(f'type {input_converter} not supported')
        else:
            return default_value
