from typing import Optional

from django.contrib import admin, messages
from django.contrib.admin import register
from django.contrib.admin.decorators import register
from django.db import models
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import path
from django.utils.translation import gettext_lazy as _


class SelfRegisterAdmin(admin.ModelAdmin):
    model_field_sets = {}
    model_title = ''
    app_label = 'admin'

    @classmethod
    def register(cls):
        if not hasattr(cls, 'model_query'):
            empty_model = type(f'{cls.__name__}_model', (CustomModelPage,),
                               {'__module__': __name__, **cls.model_field_sets,
                                'title': cls.model_title,
                                'app_label': cls.app_label

                                })
        else:
            empty_model = type(f'{cls.__name__}_model', (cls.model_query,),
                               {'__module__': __name__, 'title': cls.model_title})
        register(empty_model)(cls)


class EtcAdmin(SelfRegisterAdmin):
    """Base etc admin_pages."""

    def message_success(self, request: HttpRequest, msg: str):
        self.message_user(request, msg, messages.SUCCESS)

    def message_warning(self, request: HttpRequest, msg: str):
        self.message_user(request, msg, messages.WARNING)

    def message_error(self, request: HttpRequest, msg: str):
        self.message_user(request, msg, messages.ERROR)


class ReadonlyAdmin(EtcAdmin):
    """Read-only etc admin_pages base class."""

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
    """Base for admin_pages pages with contents based on custom models."""

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
    """Allows construction of admin_pages pages based on user input.
    Define your fields (as usual in models) and override .save() method.
    .. code-block:: python
        class MyPage(CustomModelPage):
            title = 'Test page 1'  # set page title
            # Define some fields.
            my_field = models.CharField('some title', max_length=10)
            def save(self):
                ...  # Implement data handling.
                super().save()
        # Register my page within Django admin_pages.
        MyPage.register()
    """
    title: str = _('Custom page')
    """Page title to be used."""

    app_label: str = 'admin'
    """Application label to relate page to. Default: admin_pages"""

    bound_request: Optional[HttpRequest] = None
    """Request object bound to the model"""

    bound_admin: Optional[EtcAdmin] = None
    """Django admin_pages model bound to this model."""

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
        """Registers this model page class in Django admin_pages.
        :param admin_model:
        """
        register(cls)(admin_model or CustomPageModelAdmin)

    def save(self):  # noqa
        """Heirs should implement their own save handling."""
        self.bound_admin.message_success(self.bound_request, _('Done.'))


class EmptyModel(CustomModelPage):
    pass
