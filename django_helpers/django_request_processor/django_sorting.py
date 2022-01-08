from typing import Iterable

from django.db.models import QuerySet

from django_helpers.request_processor.sorting import SortProcessor


class DjangoSorting(SortProcessor):
    def __init__(self, sort_field_name: str = 'sort_by', multi_sort_field_name: str = 'multi_sort_by', use_sorting=True,
                 use_multi_sorting=True, raise_exception: bool = False,
                 request_methods: Iterable[str] = ('GET', 'POST', 'body'), convert_bytes_to_str: bool = True,
                 convert_bytes_to_json: bool = True):
        super().__init__(sort_field_name, multi_sort_field_name, use_sorting, use_multi_sorting, raise_exception,
                         request_methods, convert_bytes_to_str, convert_bytes_to_json)

    def process_sorting(self, data: Iterable) -> Iterable:
        if isinstance(data, QuerySet):
            field_names = [accessor.original_field_name for accessor in self.access_fields]
            return data.order_by(*field_names)
        else:
            return super().process_sorting(data)







