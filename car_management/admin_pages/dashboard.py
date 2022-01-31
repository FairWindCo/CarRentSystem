from django.contrib import admin
from django.contrib.admin import ModelAdmin

from django_helpers.admin import EmptyModel


# @admin.register(EmptyModel)
class SummaryAdmin(ModelAdmin):
    change_list_template = 'admin/sale_summary_change_list.html'

    def get_changelist(self, request, **kwargs):
        return super().get_changelist(request, **kwargs)
    # date_hierarchy = 'created'

