from django.contrib import admin

from .custom_admin import CustomPageModelAdmin


class InvestorAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']


class TaxiOperatorAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']


class CounterpartAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']


class TaxiTripPageAdmin(CustomPageModelAdmin):
    autocomplete_fields = ('car', 'driver', 'counterpart')


class ProfileAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user', 'account')