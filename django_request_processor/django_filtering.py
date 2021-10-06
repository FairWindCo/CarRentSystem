from typing import Union, Callable, Iterable

from django.db.models import QuerySet

from request_processor.filtering import FilterProcessor


class DjangoFiltering(FilterProcessor):
    request_methods = ('GET', 'POST', 'body')

    def __init__(self, descriptions: Union[dict, iter, str, Callable], request_methods=request_methods, *args,
                 **kwargs):
        super().__init__(descriptions, request_methods, *args, **kwargs)

    def process_one_filter(self, data: Iterable, accessor) -> Iterable:
        if isinstance(data, QuerySet):
            form_value = accessor.get_form_value()
            return data.filter({
                accessor.object_accessor.original_field_name: form_value
            })
        else:
            return super().process_one_filter(data, accessor)
