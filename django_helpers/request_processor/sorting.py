from typing import Iterable

from django_helpers.request_processor.request_utility import RequestValue
from django_helpers.request_processor.value_utility import PrototypedValueAccessor


class SortValueAccessor(PrototypedValueAccessor):
    OPERATORS_PREFIX = ('-', '+')


class SortProcessor:
    sort_field_name_default: str = 'id'
    use_default_sorting = True

    def __init__(self,
                 sort_field_name: str = 'sort_by',
                 multi_sort_field_name: str = 'multi_sort_by',
                 use_sorting=True,
                 use_multi_sorting=True,
                 raise_exception: bool = False,
                 request_methods: Iterable[str] = ('GET', 'POST', 'body'),
                 convert_bytes_to_str: bool = True,
                 convert_bytes_to_json: bool = True):
        self.sorting_value = RequestValue(sort_field_name, self.sort_field_name_default,
                                          'str',
                                          raise_exception,
                                          request_methods,
                                          convert_bytes_to_str, convert_bytes_to_json)
        self.sorting_multi_value = RequestValue(multi_sort_field_name, '',
                                                'str',
                                                raise_exception,
                                                request_methods,
                                                convert_bytes_to_str, convert_bytes_to_json)
        self.use_sorting = use_sorting
        self.use_multi_sorting = use_multi_sorting
        self.access_fields: Iterable[SortValueAccessor] = ()

    def read_sorting_parameters_from_request(self, request):
        sorter_fields = []
        if self.use_sorting:
            self.sorting_value.get_value_from_request(request)
            sorter_fields.extend(SortValueAccessor.only_names(self.sorting_value.value))

        if self.use_multi_sorting:
            self.sorting_multi_value.get_value_from_request(request)
            if self.sorting_multi_value.is_real_value:
                sorter_fields.extend(SortValueAccessor.only_names(self.sorting_multi_value.value))

        self.access_fields = sorter_fields

    def process_sorting(self, data: Iterable) -> Iterable:
        if self.is_in_request() or self.use_default_sorting:
            for accessor in self.access_fields:
                data = self.process_one_sorting(data, accessor)
        return data

    def process_one_sorting(self, data: Iterable, accessor) -> Iterable:
        reverse_sort = True if accessor.field_prefix == '-' else False
        return sorted(data, key=lambda obj: accessor.get_result_value(obj), reverse=reverse_sort)

    def get_sort_names(self):
        return [accessor.field_name for accessor in self.access_fields]

    def is_in_request(self):
        return self.sorting_value.is_real_value | self.sorting_multi_value.is_real_value
