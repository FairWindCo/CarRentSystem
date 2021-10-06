from django.views.generic import ListView

from django_request_processor.django_filtering import DjangoFiltering
from django_request_processor.django_paging import DjangoPaging
from django_request_processor.django_serializer import DjangoSerializer
from django_request_processor.django_sorting import DjangoSorting


class UniversalFilterListView(ListView):
    filtering = None
    sorting = None
    serialize = None
    request_methods = ('GET', 'POST', 'body')
    page_request_field_name = 'page'
    per_page_request_field_name = 'per_page'
    per_page_default = 10
    use_custom_paging = True
    use_custom_order = False
    use_custom_serializer = False
    sort_field_name: str = 'sort_by'
    multi_sort_field_name: str = 'multi_sort_by'
    use_sorting = True
    use_multi_sorting = True
    raise_exception: bool = False
    convert_bytes_to_str: bool = True
    convert_bytes_to_json: bool = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.sorting is None:
            self.use_custom_order = False
        if self.serialize is None:
            self.use_custom_serializer = False

        if self.use_custom_serializer:
            self.use_custom_paging = True

        self.filter_processor = None
        if self.filtering is not None:
            self.filter_processor = DjangoFiltering(self.filtering, self.request_methods)
        self.sort_processor = DjangoSorting(self.sort_field_name,
                                            self.multi_sort_field_name,
                                            self.use_sorting,
                                            self.use_multi_sorting,
                                            self.raise_exception,
                                            self.request_methods,
                                            self.convert_bytes_to_str,
                                            self.convert_bytes_to_json)
        self.page_processor = DjangoPaging(self.page_request_field_name,
                                           self.per_page_request_field_name,
                                           self.per_page_default,
                                           self.use_custom_paging,
                                           self.raise_exception,
                                           self.request_methods,
                                           self.convert_bytes_to_str,
                                           self.convert_bytes_to_json
                                           )
        self.serialize_processor = DjangoSerializer(self.serialize)

        self.paging = None

    def get_queryset(self):
        initial_query_set = super().get_queryset()

        result_query_set = initial_query_set
        if self.filtering is not None:
            result_query_set = self.filter_processor.process_filtering(result_query_set)
        if self.use_custom_order:
            result_query_set = self.sort_processor.process_sorting(result_query_set)
        if self.use_custom_paging:
            result_query_set, self.paging = self.page_processor.get_paging(result_query_set)
        if self.use_custom_serializer:
            result_query_set = self.serialize_processor.serialize_data(result_query_set)

        return result_query_set

    def get_ordering(self):
        if self.use_custom_order:
            return None
        if self.sort_processor:
            return self.sort_processor.
        return super().get_ordering()

    def paginate_queryset(self, queryset, page_size):
        print('paging')
        if self.use_custom_paging:
            return self.page_processor.get_paging(queryset)
        else:
            return super().paginate_queryset(queryset, page_size)

    def get_paginate_by(self, queryset):
        if self.use_custom_paging:
            return None
        else:
            return super().get_paginate_by(queryset)

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True, **kwargs):
        if self.use_custom_paging:
            return self.page_processor.get_paginator()
        print('create paginator')
        paginator = super().get_paginator(queryset, per_page, orphans, allow_empty_first_page, **kwargs)
        # self.paging = self.page_processor.form_current_page_info(queryset, paginator)
        return paginator

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        print('update context')
        if self.paging:
            print('update context paging')
            context.update(self.paging)
        return context

    def request_processor(self, request):
        if self.filtering:
            self.filtering.process_filtering(request)
        self.page_processor.get_parameters_from_request(request)
        self.sort_processor.read_sorting_parameters_from_request(request)

    def get(self, request, *args, **kwargs):
        self.request_processor(request)
        return ListView.get(self, request, *args, *kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
