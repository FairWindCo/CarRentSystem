from typing import Union, Iterable, Any

from django.core.paginator import Paginator
from django.db.models import QuerySet

from request_processor.paging import PageProcessor


class DjangoPaging(PageProcessor):

    def __init__(self, raise_exception: bool = False, request_methods: Iterable[str] = ('GET', 'POST', 'body'),
                 convert_bytes_to_str: bool = True, convert_bytes_to_json: bool = True):
        super().__init__(raise_exception, request_methods, convert_bytes_to_str, convert_bytes_to_json)
        self.paginator = None

    def _extract_page(self, query_set: Union[QuerySet, Iterable, Any], page_num: int, row_per_page: int):
        if isinstance(query_set, QuerySet):
            paginator = Paginator(query_set, row_per_page)
            self.paginator = paginator
            return paginator.count, paginator.get_page(page_num)
        else:
            return super(DjangoPaging, self)._extract_page(query_set, page_num, row_per_page)
