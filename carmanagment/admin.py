from django import forms
from django.contrib import admin
from django.db.models import Q
from django.utils.timezone import now

from balance.admin import ReadOnlyModelAdmin, BalanceReadOnlyField
from balance.services import Balance
from carmanagment.custom_admin import CustomPageModelAdmin
from carmanagment.custom_models import ExpensePage, OtherExpensePage
from carmanagment.models import *


class CarAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Investor', {'fields': ('car_investor',)}),
        ('Car Model', {'fields': ('model',)}),
        ('Car Info', {'fields': (
            'name', 'year', 'mileage_at_start', 'investment', 'date_start', 'control_mileage', 'last_TO_date')})
    )
    readonly_fields = ('investment', 'date_start', 'control_mileage', 'last_TO_date')
    autocomplete_fields = ('car_investor', 'model')
    dynamic_fieldsets = {
        'Инвестиции': [('start_amount', forms.IntegerField(label='Стоимость инвестиции', min_value=0))],
    }
    ordering = ['name', 'model__name', 'model__brand__name']
    search_fields = ['name', 'model__name', 'model__brand__name']

    def get_fieldsets(self, request, obj=None):
        fs = super().get_fieldsets(request, obj)
        if obj is None:
            new_dynamic_fieldsets = getattr(self, 'dynamic_fieldsets', {})
            for set_name, field_def_list in new_dynamic_fieldsets.items():
                for field_name, field_def in field_def_list:
                    # `gf.append(field_name)` results in multiple instances of the new fields
                    fs = fs + ((set_name, {'fields': (field_name,)}),)
                    # updating base_fields seems to have the same effect
                    self.form.declared_fields.update({field_name: field_def})
        return fs

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def save_form(self, request, form, change):
        return form.save(commit=False)

    def save_model(self, request, obj, form, change):
        # obj=CarCreator.add_new_car_from_id(
        #     model_id=form.data['model'],
        #     investor_id=form.data['car_investor'],
        #     car_plate=form.data['name'],
        #     year=int(form.data['year']),
        #     mileage_at_start=int(form.data['mileage_at_start']),
        #     start_amount=int(form.data['start_amount'])
        # )
        obj.control_mileage = int(form.data['mileage_at_start'])
        obj.investment = InvestmentCarBalance(name=obj.name, create_date=now().date(),
                                              currency=Account.AccountCurrency.DOLLAR)
        obj.investment.save()
        super().save_model(request, obj, form, change)
        obj.save()
        transaction = Balance.form_transaction(Balance.INVESTMENT,
                                               [(obj.investment, None, int(form.data['start_amount']))])
        transaction.save()

    # def save_related(self, request, form, formsets, change):
    #     pass


class InvestorAdmin(ReadOnlyModelAdmin):
    ordering = ['name']
    search_fields = ['name']


class CarModelAdmin(admin.ModelAdmin):
    ordering = ['brand__name', 'name']
    search_fields = ['brand__name', 'name']


class ExpensesTypesAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

    def get_search_results(self, request, queryset, search_term):
        print("In get search results", request)
        if 'model_name' in request.GET:
            if request.GET['model_name'] == 'expensepage':
                queryset = queryset.filter(Q(type_class=ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE) | Q(
                    type_class=ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE))
            elif request.GET['model_name'] == 'otherexpensepage':
                queryset = queryset.exclude(Q(type_class=ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE) | Q(
                    type_class=ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE))
        results = super().get_search_results(request, queryset, search_term)
        return results


class CarExpenseBase(CustomPageModelAdmin):
    autocomplete_fields = ('car', 'expense_type', 'counterpart')


class OtherExpenseBase(CustomPageModelAdmin):
    autocomplete_fields = ('account', 'expense_type', 'counterpart')


# Register my page within Django admin.
class CounterpartAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']


ExpensePage.register(admin_model=CarExpenseBase)
OtherExpensePage.register(admin_model=OtherExpenseBase)
admin.site.register(Car, CarAdmin)
admin.site.register(Expenses, ReadOnlyModelAdmin)
admin.site.register(Driver, BalanceReadOnlyField)
admin.site.register(ExpensesTypes, ExpensesTypesAdmin)
admin.site.register(Investor, InvestorAdmin)
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(Counterpart, CounterpartAdmin)
admin.site.register(CarBrand)
