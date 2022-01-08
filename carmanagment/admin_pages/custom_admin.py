from django.contrib.admin.decorators import register
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.urls import path

from django_helpers.admin import EtcAdmin, CustomModelPage
from django_helpers.admin.custom_ import ChangeListSpecial


class ListAdmin(EtcAdmin):
    class Opts:
        pass

    class Cl:
        pass

    class AppConfig:
        def __init__(self, verbose_name):
            self.verbose_name = verbose_name

    actions = None
    model_field_sets = {}
    model_title = f'Custom View Page'
    use_custom_view_template = True
    use_change_list = False

    @classmethod
    def register(cls):
        if not hasattr(cls, 'model_query'):
            empty_model = type(f'{cls.__name__}_model', (CustomModelPage,),
                               {'__module__': __name__, **cls.model_field_sets, 'title': cls.model_title})
        else:
            empty_model = type(f'{cls.__name__}_model', (cls.model_query,),
                               {'__module__': __name__, 'title': cls.model_title})
        register(empty_model)(cls)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: models.Model = None) -> bool:
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_object(self, request, object_id, from_field=None):
        return super().get_object(request, object_id, from_field)

    def get_queryset(self, request):
        return []

    def get_urls(self) -> list:
        meta = self.model._meta
        patterns = [path(
            '',
            self.admin_site.admin_view(self.view_custom if self.use_custom_view_template
                                       else self.changelist_view),
            name=f'{meta.app_label}_{meta.model_name}_changelist'
        )]
        return patterns

    def get_title(self):
        return 'Custom View Page'

    def view_custom(self, request: HttpRequest) -> HttpResponse:
        title = self.get_title()
        opts = self.Opts()
        config = self.AppConfig(title)
        sortable_by = self.get_sortable_by(request)
        if self.use_change_list:
            list_display = self.get_list_display(request)
            list_display_links = self.get_list_display_links(request, list_display)
            # Add the action checkboxes if any actions are available.
            if self.get_actions(request):
                list_display = ['action_checkbox', *list_display]
            cl = ChangeListSpecial(
                request,
                self.model,
                list_display,
                list_display_links,
                self.get_list_filter(request),
                self.date_hierarchy,
                self.get_search_fields(request),
                self.get_list_select_related(request),
                self.list_per_page,
                self.list_max_show_all,
                self.list_editable,
                self,
                sortable_by,
            )
            opts = cl.opts
        else:
            cl = self.Cl()
            setattr(cl, 'opts', opts)
            setattr(cl, 'result_count', 10)
            setattr(cl, 'full_result_count', 10)
            setattr(cl, 'get_ordering_field_columns', sortable_by)
            setattr(opts, 'app_label', 'admin_pages')
            setattr(opts, 'app_config', config)
            # cl.opts.app_config.verbose_name
            setattr(opts, 'object_name', title)
        context: dict = {
            **self.admin_site.each_context(request),
            'title': title,
            'opts': opts,
            'cl': cl,
        }
        print(context)
        return TemplateResponse(request, 'test.html', context)


