import json
from json import JSONDecodeError
from typing import Iterable, Any, Callable, Union
from urllib.parse import unquote

from request_processor.value_utility import ComplexValueAccessor, PrototypedValueAccessor, PrototypedAccessor


class RequestValue(ComplexValueAccessor, PrototypedAccessor):

    def __init__(self, parameter_name: str,
                 default_value: Any = None,
                 input_converter: Union[str, Callable] = 'any',
                 raise_exception: bool = False,
                 request_methods: Iterable[str] = ('GET', 'POST', 'body'),
                 convert_bytes_to_str: bool = True,
                 convert_bytes_to_json: bool = True
                 ):
        super(RequestValue, self).__init__([parameter_name], default_value, input_converter,
                                           raise_exception=raise_exception)
        self.request_methods = request_methods
        self.input_converter = input_converter
        self.convert_bytes_to_str = convert_bytes_to_str
        self.convert_bytes_to_json = convert_bytes_to_json
        self.value = None
        self.is_real_value = False

    def get_value_from_request(self, request):
        value, self.is_real_value = self.get_from_request(request, self.field_path[0], self.default_value,
                                                          self.raise_exception_of_not_exist, self.request_methods,
                                                          self.convert_bytes_to_str, self.convert_bytes_to_json
                                                          )
        self.value = self.convert_value(value)
        return value

    @staticmethod
    def get_from_request(request, request_param_name: str, default_value: any = None,
                         raise_exception: bool = False,
                         request_methods: Iterable[str] = ('GET', 'POST', 'body'),
                         convert_bytes_to_str: bool = True,
                         convert_bytes_to_json: bool = True) -> (Any, bool):
        if request is None:
            if raise_exception:
                raise ValueError('Request is None')
            else:
                return default_value, False
        if request_param_name:
            for method_name in request_methods:
                method = ComplexValueAccessor.get_obj_member(request, method_name, None)
                if method:
                    if isinstance(method, bytes):
                        try:
                            if convert_bytes_to_str or convert_bytes_to_json:
                                method = method.decode('utf-8')
                            if convert_bytes_to_json:
                                method = json.loads(method)
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


class BiDirectionalForm(RequestValue):

    def __init__(self,
                 object_field_description: Union[dict, iter, str, Callable],
                 parameter_name: str,
                 default_value: Any = None,
                 converter_for_request_value: Union[str, Callable] = 'any',
                 raise_exception: bool = False,
                 request_methods: Iterable[str] = ('GET', 'POST', 'body'),
                 ):
        super().__init__(parameter_name, default_value, converter_for_request_value, raise_exception, request_methods)
        self.object_accessor = PrototypedValueAccessor.from_description(object_field_description)

    def get_object_value(self, obj):
        return self.object_accessor.get_value(obj)
