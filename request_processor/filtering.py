from typing import Union, Callable, Iterable

from request_processor.request_utility import BiDirectionalForm
from request_processor.value_utility import PrototypedAccessor


class FilterProcessor(PrototypedAccessor):
    def __init__(self, descriptions: Union[dict, iter, str, Callable], request_methods=('GET', 'POST', 'body'), *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.fields_descriptions = BiDirectionalForm.from_description(descriptions, request_methods=request_methods)

    def read_filters_from_request(self, request):
        for fields_description in self.fields_descriptions:
            fields_description.process_request(request)

    def process_filtering(self, data: Iterable) -> Iterable:
        for accessor in self.fields_descriptions:
            data = self.process_one_filter(data, accessor)
        return data

    def process_one_filter(self, data: Iterable, accessor) -> Iterable:
        return filter(lambda obj: self.filter_function(accessor, obj), data)

    @staticmethod
    def filter_function(accessor, obj) -> bool:
        form_value = accessor.get_form_value()
        value = accessor.get_object_value(obj)
        # print(form_value, value, form_value == value)
        return form_value == value
