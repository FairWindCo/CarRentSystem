from django.contrib import admin

from django_helpers.admin.artificial_admin_models import CustomPageModelAdmin


class InvestorAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']


class DriverAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

class CounterpartAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']


class ProfileAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user', 'account')
