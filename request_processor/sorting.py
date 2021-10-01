from typing import Iterable, Union

from request_processor.request_utility import RequestValue
from request_processor.value_utility import PrototypedValueAccessor


class SortProcessor:
    def __init__(self,
                 data_fields_for_sorting: Union[str, Iterable, dict] = "",
                 sort_field_name_default: str = 'id',
                 sort_field_name: str = 'sort_by',
                 multi_sort_field_name: str = 'multi_sort_by',
                 use_sorting=True,
                 use_multi_sorting=True,
                 raise_exception: bool = False,
                 request_methods: Iterable[str] = ('GET', 'POST', 'body'),
                 convert_bytes_to_str: bool = True,
                 convert_bytes_to_json: bool = True):
        self.sorting_value = RequestValue(sort_field_name, sort_field_name_default,
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
        self.access_fields = ()

    def read_sorting_parameters_from_request(self, request):
        sorter_fields = []
        if self.use_sorting:
            self.sorting_value.get_value_from_request(request)
            sorter_fields.append(PrototypedValueAccessor.parse_one(self.sorting_value.value))

        if self.use_multi_sorting:
            self.sorting_multi_value.get_value_from_request(request)
            if self.sorting_multi_value.is_real_value:
                sorter_fields.extend(PrototypedValueAccessor.from_description(self.sorting_multi_value.value))

        self.access_fields = sorter_fields

    def process_sorting(self, data: Iterable) -> Iterable:
        for accessor in self.access_fields:
            data = sorted(data, key=lambda obj: accessor.get_result_value(obj))
        return data
