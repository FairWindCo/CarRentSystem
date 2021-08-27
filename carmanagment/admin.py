from django.contrib import admin

# Register your models here.
from balance.admin import ReadOnlyModelAdmin, BalanceReadOnlyField
from carmanagment.models import *

admin.site.register(Car, ReadOnlyModelAdmin)
admin.site.register(Expenses, ReadOnlyModelAdmin)

admin.site.register(Driver, BalanceReadOnlyField)
admin.site.register(Investor, BalanceReadOnlyField)
admin.site.register(CarModel)
admin.site.register(CarBrand)
admin.site.register(ExpensesTypes)