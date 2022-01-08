from balance.models import AccountTransaction, Transaction
from carmanagment.views.global_menu import GlobalMainMenu
from django_helpers.django_request_processor import UniversalFilterListView


class OperationsView(UniversalFilterListView, GlobalMainMenu):
    model = AccountTransaction
    template_name = 'carmanagment/operation_list.html'
    paginate_by = 20
    filtering = (
        ('account__name__icontains', 'name'),
        ('transaction__transactionTime__gte', 'start_interval'),
        ('transaction__transactionTime__lte', 'end_interval'),
    )


class TransactionView(UniversalFilterListView, GlobalMainMenu):
    model = Transaction
    template_name = 'carmanagment/transaction_list.html'
    paginate_by = 20
    filtering = (
        ('transactionTime__gte', 'start_interval'),
        ('transactionTime__lte', 'end_interval'),
    )