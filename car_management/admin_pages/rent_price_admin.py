from django.contrib import admin


class RentPriceAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
    readonly_fields = ('replaced_by_new',)


class RentTermsAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
    readonly_fields = ('replaced_by_new',)
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Условия распределения дохода', {
            'fields': ('profit', 'fuel_compensation', 'additional_millage'),
        }),
        ('Контрольные показатели', {
            'fields': ('min_trips', 'max_millage', 'plan_amount', 'trips_control', 'millage_control', 'amount_control'),
        }),
        ('Контрольный интервал', {
            'fields': ('type_class', 'control_interval', 'control_interval_paid_distance'),
        }),
    )
