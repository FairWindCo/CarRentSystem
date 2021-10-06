from typing import Union, Iterable, Any

from django.core.paginator import Paginator
from django.db.models import QuerySet

from request_processor.paging import PageProcessor


class DjangoPaging(PageProcessor):
    page_request_field_name = 'page'
    per_page_request_field_name = 'per_page'
    per_page_default = 10
    use_paging = True

    def __init__(self,
                 page_request_field_name=page_request_field_name,
                 per_page_request_field_name=per_page_request_field_name,
                 per_page_default=per_page_default,
                 use_paging=True,
                 raise_exception: bool = False,
                 request_methods: Iterable[str] = ('GET', 'POST', 'body'), convert_bytes_to_str: bool = True,
                 convert_bytes_to_json: bool = True):
        super().__init__(page_request_field_name, per_page_request_field_name, per_page_default, use_paging,
                         raise_exception, request_methods, convert_bytes_to_str, convert_bytes_to_json)

        self.paginator = None

    def _extract_page(self, query_set: Union[QuerySet, Iterable, Any], page_num: int, row_per_page: int):
        if isinstance(query_set, QuerySet):
            paginator = Paginator(query_set, row_per_page)
            self.paginator = paginator
            return paginator.count, paginator.get_page(page_num)
        else:
            return super(DjangoPaging, self)._extract_page(query_set, page_num, row_per_page)

    def form_current_page_info(self, page_data: Union[QuerySet, Iterable] = (), paginator=None):
        if page_data is None:
            page_info = self.form_page(self.get_page_num(), self.get_per_page(), 0, ())
            page_info['paginator'] = self.paginator
            return page_info
        if isinstance(page_data, QuerySet):
            page_info = self.form_page(self.get_page_num(), self.get_per_page(), page_data.count(), page_data)
            page_info['paginator'] = self.paginator
            return page_info
        return super(DjangoPaging, self).form_current_page_info(page_data, paginator)

    def get_paginator(self):
        return self.paginator
