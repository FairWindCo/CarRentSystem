from typing import Optional

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.decorators import register
from django.contrib.admin.views.main import ChangeList
from django.db import models
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.translation import gettext_lazy as _

from utils.custom_ import ChangeListSpecial


class EtcAdmin(admin.ModelAdmin):
    """Base etc admin."""

    def message_success(self, request: HttpRequest, msg: str):
        self.message_user(request, msg, messages.SUCCESS)

    def message_warning(self, request: HttpRequest, msg: str):
        self.message_user(request, msg, messages.WARNING)

    def message_error(self, request: HttpRequest, msg: str):
        self.message_user(request, msg, messages.ERROR)


class ReadonlyAdmin(EtcAdmin):
    """Read-only etc admin base class."""

    view_on_site: bool = False
    actions = None

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: models.Model = None) -> bool:
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changeform_view(
            self,
            request: HttpRequest,
            object_id: int = None,
            form_url: str = '',
            extra_context: dict = None
    ) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context.update({
            'show_save_and_continue': False,
            'show_save': False,
        })
        return super().changeform_view(request, object_id, extra_context=extra_context)


class CustomPageModelAdmin(ReadonlyAdmin):
    """Base for admin pages with contents based on custom models."""

    def get_urls(self) -> list:
        meta = self.model._meta
        patterns = [path(
            '',
            self.admin_site.admin_view(self.view_custom),
            name=f'{meta.app_label}_{meta.model_name}_changelist'
        )]
        return patterns

    def has_add_permission(self, request: HttpRequest) -> bool:
        return True

    def view_custom(self, request: HttpRequest) -> HttpResponse:
        context: dict = {
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'title': self.model._meta.verbose_name,
        }
        return self._changeform_view(request, object_id=None, form_url='', extra_context=context)

    def response_add(self, request: HttpRequest, obj: 'CustomModelPage', post_url_continue=None):
        return HttpResponseRedirect(request.path)

    def save_model(self, request: HttpRequest, obj: 'CustomModelPage', form, change):
        obj.bound_request = request
        obj.bound_admin = self
        obj.save()


class CustomModelPage(models.Model):
    """Allows construction of admin pages based on user input.
    Define your fields (as usual in models) and override .save() method.
    .. code-block:: python
        class MyPage(CustomModelPage):
            title = 'Test page 1'  # set page title
            # Define some fields.
            my_field = models.CharField('some title', max_length=10)
            def save(self):
                ...  # Implement data handling.
                super().save()
        # Register my page within Django admin.
        MyPage.register()
    """
    title: str = _('Custom page')
    """Page title to be used."""

    app_label: str = 'admin'
    """Application label to relate page to. Default: admin"""

    bound_request: Optional[HttpRequest] = None
    """Request object bound to the model"""

    bound_admin: Optional[EtcAdmin] = None
    """Django admin model bound to this model."""

    class Meta:
        abstract = True
        managed = False

    @classmethod
    def __init_subclass__(cls) -> None:
        meta = cls.Meta
        meta.verbose_name = meta.verbose_name_plural = cls.title
        meta.app_label = cls.app_label
        super().__init_subclass__()

    @classmethod
    def register(cls, *, admin_model: CustomPageModelAdmin = None):
        """Registers this model page class in Django admin.
        :param admin_model:
        """
        register(cls)(admin_model or CustomPageModelAdmin)

    def save(self):  # noqa
        """Heirs should implement their own save handling."""
        self.bound_admin.message_success(self.bound_request, _('Done.'))


class AddDynamicFieldMixin(admin.ModelAdmin):
    def get_fieldsets(self, request, obj=None):
        fs = super().get_fieldsets(request, obj)
        new_dynamic_fieldsets = getattr(self, 'dynamic_fieldsets', {})
        for set_name, field_def_list in new_dynamic_fieldsets.items():
            for field_name, field_def in field_def_list:
                # `gf.append(field_name)` results in multiple instances of the new fields
                fs = fs + ((set_name, {'fields': (field_name,)}),)
                # updating base_fields seems to have the same effect
                self.form.declared_fields.update({field_name: field_def})
        return fs

    def get_fields(self, request, obj=None):
        gf = super().get_fields(request, obj)
        new_dynamic_fields = getattr(self, 'dynamic_fields', [])
        # without updating get_fields, the admin form will display w/o any new fields
        # without updating base_fields or declared_fields, django will throw an error: django.core.exceptions.FieldError: Unknown field(s) (test) specified for MyModel. Check fields/fieldsets/exclude attributes of class MyModelAdmin.
        for field_name, field_def in new_dynamic_fields:
            # `gf.append(field_name)` results in multiple instances of the new fields
            gf = gf + [field_name]
            # updating base_fields seems to have the same effect
            self.form.declared_fields.update({field_name: field_def})
        return gf


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
            self.admin_site.admin_view(self.view_custom if self.use_custom_view_template else self.changelist_view),
            name=f'{meta.app_label}_{meta.model_name}_changelist'
        )]
        return patterns

    def get_title(self):
        return 'Custom View Page'

    def view_custom(self, request: HttpRequest) -> HttpResponse:
        title = self.get_title()
        cl = self.Cl()
        opts = self.Opts()
        config = self.AppConfig(title)
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        # Add the action checkboxes if any actions are available.
        if self.get_actions(request):
            list_display = ['action_checkbox', *list_display]
        sortable_by = self.get_sortable_by(request)
        if self.use_change_list:
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

        setattr(cl, 'opts', opts)
        setattr(cl, 'result_count', 0)
        setattr(cl, 'full_result_count', 0)
        setattr(cl, 'get_ordering_field_columns', '')
        setattr(opts, 'app_label', 'admin')
        setattr(opts, 'app_config', config)
        # cl.opts.app_config.verbose_name
        setattr(opts, 'object_name', title)
        context: dict = {
            **self.admin_site.each_context(request),
            'title': title,
            'opts': opts,
            'cl': cl,

        }
        return TemplateResponse(request, 'test.html', context)


def get_model_fields(model):
    fields = {}
    options = model._meta
    for field in sorted(options.concrete_fields + options.many_to_many):
        fields[field.name] = field
    return fields
