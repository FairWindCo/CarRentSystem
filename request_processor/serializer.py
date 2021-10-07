from typing import Union, Callable, Iterable, Any

from request_processor.value_utility import PrototypedValueAccessor, simplify_value


class SerializeProcessor:

    def __init__(self, descriptions: Union[dict, iter, str, Callable]):
        super(SerializeProcessor, self).__init__()
        self.descriptions = descriptions
        self.field_serializer = PrototypedValueAccessor.from_description(descriptions)

    def serialize_element(self, element: Any) -> Any:
        if isinstance(self.descriptions, Callable):
            return self.descriptions(element)

        if not self.field_serializer:
            return simplify_value(element)
        result_dict = {}
        for serializer in self.field_serializer:
            key, value = serializer.get_result_value(element)
            result_dict.update({key: value})
        return result_dict

    def serialize_data(self, data: Union[Iterable, Any]):
        if isinstance(data, Iterable):
            return [self.serialize_element(element) for element in data]
        else:
            return self.serialize_element(data)
