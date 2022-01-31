from django.contrib import admin

from balance.admin import ReadOnlyModelAdmin, BalanceReadOnlyField
from car_management.admin_pages import *
from car_management.admin_pages.accounting_admin import DriverAdmin
from car_management.admin_pages.rent_price_admin import RentPriceAdmin, RentTermsAdmin
from car_management.models import *
from car_management.models import RentPrice

ExpensePage.register(admin_model=CarExpenseBase)
OtherExpensePage.register(admin_model=OtherExpenseBase)
# подключение авто
CarAddPage.register(admin_model=CarAddPageAdmin)
# перевод суммы прибыли на счет инвестора (со списанием в пользу фирмы ее части)
CarRentPage.register()
# Запись денег за брендирование
MoveCashPage.register()
InsertCashPage.register()
# EmptyModel.register(admin_model=ListAdmin)
# ListAdmin.register()
# MyList.register()
admin.site.register(Car, CarAdmin)
admin.site.register(Expenses, ReadOnlyModelAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(ExpensesTypes, ExpensesTypesAdmin)
admin.site.register(Investor, InvestorAdmin)
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(Counterpart, CounterpartAdmin)
admin.site.register(CarBrand)
admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(CarInsurance, CarInsuranceAdmin)
# ReturnCarRentPage.register(admin_model=ReturnCarRentPageAdmin)
admin.site.register(RentPrice, RentPriceAdmin)
admin.site.register(RentTerms, RentTermsAdmin)
