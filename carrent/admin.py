from django.contrib import admin

# Register your models here.
from carmanagment.models import CarSchedule
from carrent.admin_pages import AddDepositCarRentPage, AddDepositCarRentPageAdmin, PenaltyDepositCarRentPage, \
    PenaltyDepositCarRentPageAdmin
from carrent.admin_pages.admin_wizard import ReturnCarRentAdmin, CarRentAdmin

admin.site.register(CarSchedule, CarRentAdmin)
AddDepositCarRentPage.register(admin_model=AddDepositCarRentPageAdmin)
PenaltyDepositCarRentPage.register(admin_model=PenaltyDepositCarRentPageAdmin)
ReturnCarRentAdmin.register()