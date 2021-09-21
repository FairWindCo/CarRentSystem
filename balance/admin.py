from django.contrib import admin

# Register your models here.
from balance.models import *


class ReadOnlyModelAdmin(admin.ModelAdmin):

    # Prevent deletion from admin portal
    def has_delete_permission(self, request, obj=None):
        return False

    # Prevent adding from admin portal
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class BalanceReadOnlyField(admin.ModelAdmin):
    readonly_fields = ['last_period_balance']
    ordering = ['name']
    search_fields = ['name']


class BalanceModel(BalanceReadOnlyField, ReadOnlyModelAdmin):
    pass


class TransactionOperation(ReadOnlyModelAdmin):
    list_display = ('transaction', 'account', 'cents_amount', 'comment')
    list_filter = ('account__name',)
    ordering = ['transaction__transactionTime', ]
    search_fields = ['account__name', ]


admin.site.register(Account, BalanceModel)
admin.site.register(AccountStatement, ReadOnlyModelAdmin)
admin.site.register(Transaction, ReadOnlyModelAdmin)
admin.site.register(AccountTransaction, TransactionOperation)
