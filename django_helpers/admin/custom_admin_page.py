from django.conf.urls import url
from django.contrib.admin import ModelAdmin
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views import View

from django_helpers.admin import SelfRegisterAdmin, wrap
from django_helpers.admin.utility_classes import MyCl


# Класс для переопределения стандартных URL для админки
# Имеет встроенное поле redefined_urls словарь:
# шаблон -> (view, name_for_reverse)
class RedefineUrlAdmin(SelfRegisterAdmin):
    redefined_urls = {}

    def get_urls(self):
        urlpatterns = []
        for pattern, value in self.redefined_urls.items():
            urlpatterns += [url(pattern, wrap(value[0], self), name=value[1])]
        urlpatterns += super().get_urls()
        return urlpatterns


class CustomizeAdmin(SelfRegisterAdmin):
    title = 'wizard'

    custom_list_view = None
    custom_change_view = None
    result_chane_url = 'admin:%s_%s_changelist'
    result_add_url = 'admin:%s_%s_changelist'
    custom_delete_view = None
    custom_add_view = None

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context)

    def render_view_to_str(self, view, request, object_id=None, **extra_context):
        if view is None:
            return None
        if isinstance(view, type):
            return view.as_view()(request, object_id, **extra_context)
        elif callable(view):
            return view(request)
        else:
            return view

    def custom_view_wrapper(self, request, object_id=None, extra_context: dict = None):
        if extra_context is None:
            extra_context = {}
        if object_id is None and self.custom_add_view is not None:
            rendered_view = self.render_view_to_str(self.custom_add_view, request, None, **extra_context)
            result_url = self.result_add_url
        else:
            rendered_view = self.render_view_to_str(self.custom_change_view, request, object_id, **extra_context)
            result_url = self.result_chane_url

        if rendered_view is None:
            return HttpResponseRedirect(
                reverse(result_url % (self.model._meta.app_label, self.model._meta.model_name)))

        render_str = rendered_view.rendered_content
        cl = MyCl('test')
        context = {**self.admin_site.each_context(request),
                   'title': self.title,
                   'preserved_filters': self.get_preserved_filters(request),
                   'app_label': 'admin', 'cl': cl,
                   'opts': cl.opts,
                   'view_extra': render_str}
        context.update(extra_context or {})

        return TemplateResponse(request,
                                "django_helpers/custom_page.html", context)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if self.custom_change_view:
            return self.custom_view_wrapper(request, object_id, extra_context)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        if self.custom_add_view:
            return self.custom_view_wrapper(request, None, extra_context)
        return super().add_view(request, form_url, extra_context)


