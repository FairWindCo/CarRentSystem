from django import forms
from django.contrib import admin

# Register your models here.
from balance.admin import ReadOnlyModelAdmin, BalanceReadOnlyField
from carmanagment.models import *


class AddDynamicFieldMixin:
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


class CarAdmin(AddDynamicFieldMixin, admin.ModelAdmin):
    fieldsets = (
        ('Investor', {'fields': ('car_investor',)}),
        ('Car Model', {'fields': ('model',)}),
        ('Car Info', {'fields': ('name', 'year', 'mileage_at_start')})
    )

    autocomplete_fields = ('car_investor', 'model')
    dynamic_fieldsets = {
        'Инвестиции': [('start_amount', forms.IntegerField(label='Стоимость инвестиции', min_value=0))],
    }

    # Prevent deletion from admin portal

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        return form


class InvestorAdmin(ReadOnlyModelAdmin):
    ordering = ['name']
    search_fields = ['name']


class CarModelAdmin(admin.ModelAdmin):
    ordering = ['brand__name', 'name']
    search_fields = ['brand__name', 'name']


admin.site.register(Car, CarAdmin)
admin.site.register(Expenses, ReadOnlyModelAdmin)

admin.site.register(Driver, BalanceReadOnlyField)
admin.site.register(Investor, InvestorAdmin)
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(CarBrand)
admin.site.register(ExpensesTypes)
