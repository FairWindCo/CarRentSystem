from django.contrib import admin

from balance.admin import ReadOnlyModelAdmin, BalanceReadOnlyField
from carmanagment.admin_pages import *
from carmanagment.models import *


ExpensePage.register(admin_model=CarExpenseBase)
OtherExpensePage.register(admin_model=OtherExpenseBase)
CarAddPage.register(admin_model=CarAddPageAdmin)
TaxiTripPage.register(admin_model=TaxiTripPageAdmin)
CarRentPage.register()
MoveCashPage.register()
InsertCashPage.register()
# EmptyModel.register(admin_model=ListAdmin)
# ListAdmin.register()
# MyList.register()
admin.site.register(Car, CarAdmin)
admin.site.register(Expenses, ReadOnlyModelAdmin)
admin.site.register(Driver, BalanceReadOnlyField)
admin.site.register(ExpensesTypes, ExpensesTypesAdmin)
admin.site.register(Investor, InvestorAdmin)
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(Counterpart, CounterpartAdmin)
admin.site.register(TaxiOperator, TaxiOperatorAdmin)
admin.site.register(CarsInOperator, CarInTaxiAdmin)
admin.site.register(CarBrand)
admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(CarInsurance, CarInsuranceAdmin)
admin.site.register(CarSchedule)
admin.site.register(DriversSchedule)