from typing import Iterable, Union, Any

from django_helpers.request_processor.request_utility import RequestValue
from django_helpers.request_processor.value_utility import TypeValueProcessor


class PageProcessor:
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
                 request_methods: Iterable[str] = ('GET', 'POST', 'body'),
                 convert_bytes_to_str: bool = True,
                 convert_bytes_to_json: bool = True):
        self.page_request = RequestValue(page_request_field_name, 1, 'int', raise_exception, request_methods,
                                         convert_bytes_to_str, convert_bytes_to_json)
        self.per_page_request = RequestValue(per_page_request_field_name, per_page_default, 'int',
                                             raise_exception, request_methods, convert_bytes_to_str,
                                             convert_bytes_to_json)
        self.use_paging = use_paging
        self.page = self.form_page()

    def form_page(self, current_page: int = 0, per_page: int = 0, count: int = 0, page_data: Iterable = ()):
        result = {
            'page_num': current_page,
            'per_page': per_page if per_page > 0 else self.per_page_default,
            'page_count': int(count / per_page) + 1 if per_page > 0 else 0,
            'count': count,
            'page': page_data,
            'page_obj': page_data,
            'paging': self.use_paging
        }
        result.update(self.get_aditional_fields())
        return result

    def form_current_page_info(self, page_data: Iterable = (), paginator=None):
        if page_data is None:
            page_info = self.form_page(self.get_page_num(), self.get_per_page(), 0, ())
        else:
            page_info = self.form_page(self.get_page_num(), self.get_per_page(), len(page_data), page_data)
        page_info['paginator'] = paginator
        return page_info

    def get_aditional_fields(self):
        return {}

    def get_parameters_from_request(self, request):
        self.page_request.get_value_from_request(request)
        self.per_page_request.get_value_from_request(request)

    def get_per_page(self):
        return abs(self.per_page_request.value if self.page_request.is_real_value else self.per_page_default)

    def get_page_num(self):
        return abs(self.page_request.value if self.page_request.is_real_value else 1)

    def get_paging(self, data: Union[Iterable, Any]):
        if data is None:
            self.page = self.form_page()
            return (), self.page
        row_per_page = self.get_per_page()
        page_num = self.get_page_num()
        if not self.use_paging:
            self.page = self.form_page(per_page=row_per_page, page_data=data)
            page_data = data
        else:
            count, page_data = self._extract_page(data, page_num, row_per_page)
            self.page = self.form_page(page_num, row_per_page, count, page_data)
        return page_data, self.page

    def _extract_page(self, data: Union[Iterable, Any], page_num: int, row_per_page: int):
        if TypeValueProcessor.is_not_string_sequence(data):
            start_row = (page_num - 1) * row_per_page
            page_data = data[start_row:start_row + row_per_page]
            count = len(data)
            return count, page_data
        else:
            return 1, (data,)
