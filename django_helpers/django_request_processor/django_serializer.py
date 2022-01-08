from typing import Union, Iterable, Any

from django.db.models import QuerySet

from django_helpers.request_processor import SerializeProcessor


class DjangoSerializer(SerializeProcessor):

    def serialize_data(self, data: Union[QuerySet, Iterable, Any]):
        if isinstance(data, QuerySet):
            data = list(data.all())
        return super().serialize_data(data)
