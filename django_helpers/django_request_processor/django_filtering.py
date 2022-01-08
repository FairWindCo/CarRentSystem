from typing import Union, Callable, Iterable

from django.db.models import QuerySet

from django_helpers.request_processor.filtering import FilterProcessor


class DjangoFiltering(FilterProcessor):
    request_methods = ('GET', 'POST', 'body')

    def __init__(self, descriptions: Union[dict, iter, str, Callable], request_methods=request_methods, *args,
                 **kwargs):
        super().__init__(descriptions, request_methods, *args, **kwargs)

    def process_one_filter(self, data: Iterable, accessor) -> Iterable:
        if isinstance(data, QuerySet):
            filter_ = accessor.get_filed_name_and_form_value_pair()
            if filter_ is not None:
                return data.filter(**filter_)
            else:
                return data
        else:
            return super().process_one_filter(data, accessor)
