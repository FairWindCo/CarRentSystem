from django.contrib import admin

# Register your models here.
from car_rent.admin_pages.taxi_operator_admin import TaxiOperatorAdmin
from car_rent.models import CarSchedule, TaxiOperator, CarsInOperator
from car_rent.admin_pages import AddDepositCarRentPage, AddDepositCarRentPageAdmin, PenaltyDepositCarRentPage, \
    PenaltyDepositCarRentPageAdmin
from car_rent.admin_pages.admin_wizard import ReturnCarRentAdmin, CarRentAdmin
from car_rent.admin_pages.branding_admin import BrandingAddPage, BrandingAddAdmin

admin.site.register(TaxiOperator, TaxiOperatorAdmin)
admin.site.register(CarSchedule, CarRentAdmin)
admin.site.register(CarsInOperator)

AddDepositCarRentPage.register(admin_model=AddDepositCarRentPageAdmin)
PenaltyDepositCarRentPage.register(admin_model=PenaltyDepositCarRentPageAdmin)
ReturnCarRentAdmin.register()

# ручное добавление поездки
BrandingAddPage.register(admin_model=BrandingAddAdmin)
