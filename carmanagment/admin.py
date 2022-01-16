from django.contrib import admin

from balance.admin import ReadOnlyModelAdmin, BalanceReadOnlyField
from carmanagment.admin_pages import *
from carmanagment.models import *
from carmanagment.models import RentPrice

ExpensePage.register(admin_model=CarExpenseBase)
OtherExpensePage.register(admin_model=OtherExpenseBase)
# подключение авто
CarAddPage.register(admin_model=CarAddPageAdmin)
# ручное добавление поездки
TaxiTripPage.register(admin_model=TaxiTripPageAdmin)
# перевод суммы прибыли на счет инвестора (со списанием в пользу фирмы ее части)
CarRentPage.register()
# Запись денег за брендирование
BrandingAddPage.register(admin_model=BrandingAddAdmin)

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
admin.site.register(DriversSchedule)
admin.site.register(RentPrice)
# ReturnCarRentPage.register(admin_model=ReturnCarRentPageAdmin)
