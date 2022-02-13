from django.contrib.auth.mixins import LoginRequiredMixin

from balance.models import AccountTransaction, Transaction
from car_management.views.global_menu import GlobalMainMenu
from django_helpers.django_request_processor import UniversalFilterListView


class OperationsView(LoginRequiredMixin, UniversalFilterListView, GlobalMainMenu):
    model = AccountTransaction
    login_url = '/admin/login/'
    template_name = 'carmanagment/operation_list.html'
    paginate_by = 20
    filtering = (
        ('account__name__icontains', 'name'),
        ('transaction__transactionTime__gte', 'start_interval'),
        ('transaction__transactionTime__lte', 'end_interval'),
    )


class TransactionView(LoginRequiredMixin, UniversalFilterListView, GlobalMainMenu):
    model = Transaction
    login_url = '/admin/login/'
    template_name = 'carmanagment/transaction_list.html'
    paginate_by = 20
    filtering = (
        ('transactionTime__gte', 'start_interval'),
        ('transactionTime__lte', 'end_interval'),
    )