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


class BiDirectionalForm(PrototypedAccessor):
    request_methods = ('GET', 'POST', 'body')

    def __init__(self, field_name: Union[str, int], default_value: Any = None,
                 value_convertor: Union[str, Callable] = 'any', form_field_name: str = None,
                 form_convertor: Union[str, Callable] = 'any', can_execute_callable: bool = True,
                 can_execute_method: bool = True, ignore_hidden: bool = False, remove_suffix: bool = True,
                 raise_exception: bool = False, convert_bytes_to_str: bool = True, convert_bytes_to_json: bool = True,
                 request_methods: Iterable[str] = request_methods, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object_accessor = PrototypedValueAccessor(field_name, default_value, value_convertor, form_field_name,
                                                       can_execute_callable, can_execute_method, ignore_hidden,
                                                       remove_suffix)
        self.form_accessor = RequestValue(form_field_name, default_value, form_convertor, raise_exception,
                                          request_methods,
                                          convert_bytes_to_str, convert_bytes_to_json)

    def process_request(self, request):
        self.form_accessor.get_value_from_request(request)

    def get_object_value(self, obj):
        return self.object_accessor.get_value(obj)

    def set_object_value_from_form(self, obj):
        return self.object_accessor.modify_object_member(obj, self.form_accessor.value)

    def get_form_value(self):
        return self.form_accessor.value
