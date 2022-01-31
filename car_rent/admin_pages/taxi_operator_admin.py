from django.contrib import admin


class TaxiOperatorAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
