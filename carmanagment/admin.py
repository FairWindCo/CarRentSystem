from django.contrib import admin
from django.db.models import Q

from balance.admin import ReadOnlyModelAdmin, BalanceReadOnlyField
from carmanagment.custom_admin import CustomPageModelAdmin
from carmanagment.custom_models import ExpensePage, OtherExpensePage, CarAddPage, TaxiTripPage
from carmanagment.models import *


class CarAdmin(admin.ModelAdmin):
    readonly_fields = (
        'currency', 'last_period_balance', 'car_investor', 'model', 'investment', 'date_start', 'name', 'year',
        'mileage_at_start', 'investment')
    ordering = ['name', 'model__name', 'model__brand__name']
    search_fields = ['name', 'model__name', 'model__brand__name']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False


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


class CarAddPageAdmin(CustomPageModelAdmin):
    autocomplete_fields = ('investor', 'car_model')


class TaxiTripPageAdmin(CustomPageModelAdmin):
    autocomplete_fields = ('car', 'driver', 'counterpart')


ExpensePage.register(admin_model=CarExpenseBase)
OtherExpensePage.register(admin_model=OtherExpenseBase)
CarAddPage.register(admin_model=CarAddPageAdmin)
TaxiTripPage.register(admin_model=TaxiTripPageAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Expenses, ReadOnlyModelAdmin)
admin.site.register(Driver, BalanceReadOnlyField)
admin.site.register(ExpensesTypes, ExpensesTypesAdmin)
admin.site.register(Investor, InvestorAdmin)
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(Counterpart, CounterpartAdmin)
admin.site.register(CarBrand)
