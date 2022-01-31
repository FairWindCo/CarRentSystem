from django.contrib import admin

# Register your models here.
from trips.admin_pages.taxitrip import TaxiTripPage, TaxiTripPageAdmin

TaxiTripPage.register(admin_model=TaxiTripPageAdmin)
