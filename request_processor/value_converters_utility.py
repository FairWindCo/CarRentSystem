import json
import sys
from datetime import datetime, date, time, timedelta
from inspect import ismethod
from json import JSONDecodeError

from typing import Union, Callable, Any, Optional

if sys.version_info < (3, 7, 0):
    from collections import Sequence
    from collections.abc import Mapping
else:
    from collections.abc import Sequence
    from collections import Mapping

import pytz


class TypeValueProcessor:
    primitiveTypes = (int, float, bool, str)
    datetimeTypes = (date, datetime, time, timedelta)

    @staticmethod
    def is_primitive(obj):
        return isinstance(obj, TypeValueProcessor.primitiveTypes)

    @staticmethod
    def is_datetime(obj):
        return isinstance(obj, TypeValueProcessor.datetimeTypes)

    @staticmethod
    def is_sequence(obj):
        return isinstance(obj, Sequence) or hasattr(obj, '__iter__')

    @staticmethod
    def is_not_string_sequence(obj):
        return not isinstance(obj, str) and TypeValueProcessor.is_sequence(obj)

    @staticmethod
    def is_dict(obj):
        return isinstance(obj, Mapping)


def str_to_value(value: str, input_converter: Union[str, Callable],
                 default_value: Any) -> Any:
    if not input_converter:
        return value
    elif isinstance(input_converter, Callable):
        return input_converter(value, default_value)
    elif isinstance(input_converter, str):
        if input_converter == 'any':
            return value
        elif input_converter == 'int':
            return int(value)
        elif input_converter == 'float':
            return float(value)
        elif input_converter == 'str':
            return str(value)
        elif input_converter == 'bool':
            return True if value.lower() in ['true', '1', 't'] else False
        elif input_converter == 'timestamp':
            return datetime.fromtimestamp(float(value))
        elif input_converter.startswith('timestamp_'):
            time_zone_name = input_converter[len('timestamp_'):]
            tz = pytz.timezone(time_zone_name)
            return datetime.fromtimestamp(float(value), tz)
        elif input_converter == 'iso_datetime':
            return datetime.fromisoformat(value)
        elif input_converter.startswith('datetime_'):
            format_str = input_converter[len('datetime_'):]
            return datetime.strptime(value, format_str)
        elif input_converter == 'json':
            return json.loads(value)
    raise ValueError(f'type {input_converter} not supported')


def str_to_value_without_exception(value: str, input_converter: Union[str, Callable],
                                   default_value: Any) -> Any:
    try:
        return str_to_value(value, input_converter, default_value)
    except ValueError or JSONDecodeError:
        return default_value


def simple_value_to_str(value: Any, converter: Union[str, Callable]) -> str:
    if not converter:
        return str(value)
    elif isinstance(converter, Callable):
        return converter(value)
    elif isinstance(converter, str):
        if converter.startswith('format_'):
            format_str = converter[len('format_'):]
            return format_str.format(value)
        elif converter == 'bool_1':
            return '1' if value else '0'
        elif converter == 'bool_T':
            return 'T' if value else 'F'
        elif converter == 'bool_True':
            return 'True' if value else 'False'
        elif converter == 'bool_true':
            return 'true' if value else 'false'
        elif converter == 'timestamp':
            return value.timestamp()
        elif converter.startswith('iso_'):
            sep = converter[len('iso_'):]
            return value.isoformat(sep)
        elif converter.startswith('datetime_'):
            format_str = converter[len('datetime_'):]
            return value.strftime(format_str)
        elif converter == 'json':
            return json.dumps(value)
    return str(value)


def simplify_value(obj: Any, class_field_name: str = None) -> Optional[Union[dict, list, float, bool, str, int]]:
    if obj is None:
        return None
    if TypeValueProcessor.is_primitive(obj):  # process primitives like int, float, bool, str
        return obj
    if hasattr(obj, "_ast"):  # abstract syntax tree
        return simplify_value(getattr(obj, "_ast"))
    if TypeValueProcessor.is_not_string_sequence(obj):  # sequence
        return [simplify_value(v) for v in obj]
    if TypeValueProcessor.is_dict(obj):  # dict
        return {key: simplify_value(value)
                for key, value in obj.__dict__.items()
                if not callable(value) and not key.startswith('_')}
    # is not iterable, not primitive and not dict may be class
    result = {}
    if hasattr(obj, '__dict__'):
        result = {key: simplify_value(value)
                  for key, value in obj.__dict__.items()
                  if not callable(value) and not key.startswith('_')}
    if hasattr(obj, '__slots__'):
        result = {key: simplify_value(value)
                  for key, value in obj.__slots__.items()
                  if not callable(value) and not key.startswith('_')}
    if result and class_field_name is not None and hasattr(obj, "__class__"):
        result[class_field_name] = obj.__class__.__name__
    return result


class PrototypeDescription:
    OPERATORS_SUFFIX = ('__exact', '__iexact', '__contains', '__icontains', '__in', '__gt', '__gte', '__lt',
                        '__lte', '__startswith', '__istartswith', '__endswith', '__iendswith', '__range',
                        '__date', '__yesr', '__iso_year', '__month', '__day', '__week', '__week_day',
                        '__iso_week_day', '__quarter', '__time', '__hour', '__minute', '__second', '__regex',
                        '__iregex')

    description_field_separator = '::'
    description_separator = ','
    field_separator = '__'

    def __init__(self,
                 name: Union[str, int],
                 default_value: Any = None,
                 convertor: Union[str, Callable] = 'any',
                 result_field_name: str = None,
                 can_execute_callable: bool = True,
                 can_execute_method: bool = True,
                 ignore_hidden: bool = False,
                 remove_suffix: bool = True,
                 *args, **kwargs):
        self.field_name = name
        self.convertor = convertor
        self.result_field_name = result_field_name if result_field_name else name
        self.can_execute_callable = can_execute_callable
        self.can_execute_method = can_execute_method
        self.ignore_hidden = ignore_hidden
        self.convertor_args = args
        self.convertor_kwargs = kwargs
        self.default_value = default_value
        self.remove_suffix = remove_suffix

        self.field_path, self.field_suffix = self.convert_field_name_to_field_path(name, remove_suffix)

    @classmethod
    def convert_field_name_to_field_path(cls, field_name: str, remove_suffix: bool = True):
        suffix = None
        if remove_suffix:
            suffix_position = -1
            for suffix_ in cls.OPERATORS_SUFFIX:
                if field_name.endswith(suffix_):
                    suffix = suffix_
                    suffix_position = len(field_name) - len(suffix_)
                    break
            if suffix:
                field_name = field_name[:suffix_position]

        if field_name.find(cls.field_separator) > 0:
            field_path = field_name.split(cls.field_separator)
        else:
            field_path = [field_name]
        return field_path, suffix

    @classmethod
    def parse_one(cls, description: Union[dict, iter, str], name=None):
        if isinstance(description, str):
            if description.find(cls.description_field_separator) > 0:
                description_elem = [el.strip() for el in description.split(cls.description_field_separator)]
                return cls(name, *description_elem) if name else cls(*description_elem)
            else:
                return cls(name, description) if name else cls(description)
        elif isinstance(description, int):
            return cls(name, description) if name else cls(description)
        elif TypeValueProcessor.is_dict(description):
            if name:
                return cls(name, **description)
            else:
                name = description.pop('field_name')
                return cls(name, **description)
        elif TypeValueProcessor.is_sequence(description):
            return cls(name, *description) if name else cls(*description)
        elif name and not description:
            return cls(name)
        else:
            return None

    @classmethod
    def from_description(cls, description: Union[dict, iter, str, Callable]) -> iter:
        if isinstance(description, str):
            if description.find(cls.description_separator) > 0:
                return [cls.parse_one(string_description.strip()) for string_description in
                        description.split(cls.description_separator)]
            else:
                return [cls.parse_one(description)]
        elif isinstance(description, int):
            return cls(description)
        elif TypeValueProcessor.is_dict(description):
            return [cls.parse_one(attributes, field_name) for field_name, attributes in description.items()]
        elif TypeValueProcessor.is_sequence(description):
            return [cls.parse_one(description_element) for description_element in description]
        elif isinstance(description, Callable):
            return description()
        else:
            return []

    @classmethod
    def get_obj_member(cls, obj: Any, member_name: Union[str, int], default_val: Any = None,
                       ignore_hidden=False) -> Any:
        if obj and member_name:
            if TypeValueProcessor.is_primitive(obj):
                return default_val
            if TypeValueProcessor.is_not_string_sequence(obj) and isinstance(member_name, (int, str)):
                try:
                    index = int(member_name)
                except ValueError:
                    index = None
                if index is not None:
                    return default_val if len(obj) <= abs(index) else obj[index]
            if isinstance(member_name, str):
                if member_name.startswith('_') and ignore_hidden:
                    return default_val
                if TypeValueProcessor.is_dict(obj):
                    return obj.get(member_name, default_val)
                if hasattr(obj, member_name):
                    val = getattr(obj, member_name)
                    return val
        return default_val

    def get_object_member(self, obj: Any):
        if obj and not TypeValueProcessor.is_primitive(obj):
            for name in self.field_path:
                obj = self.get_obj_member(obj, name, self.default_value, self.ignore_hidden)
                if self.can_execute_callable and callable(obj):
                    if ismethod(obj) and self.can_execute_method:
                        obj = obj()
                if TypeValueProcessor.is_primitive(obj):
                    break
        return obj

    def get_result_value(self, obj):
        value = self.get_object_member(obj)
        if value and self.convertor:
            if isinstance(value, str):
                value = str_to_value_without_exception(value, self.convertor, self.default_value)
            elif TypeValueProcessor.is_primitive(value) or TypeValueProcessor.is_datetime(value):
                value = simple_value_to_str(value, self.convertor)
            else:
                value = simplify_value(value)
        return self.result_field_name, value
