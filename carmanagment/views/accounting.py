from balance.models import CashBox
from carmanagment.models import Car, Investor, Driver, Counterpart, TaxiOperator
from carmanagment.views.global_menu import GlobalMainMenu
from django_request_processor.django_list_view import UniversalFilterListView


class ViewCarAccount(UniversalFilterListView, GlobalMainMenu):
    model = Car
    template_name = 'carmanagment/acccount_list.html'
    paginate_by = 20
    filtering = (
        ('name',),
    )


class ViewCarInvestmentAccount(ViewCarAccount, GlobalMainMenu):
    model = Car
    template_name = 'carmanagment/inest_list.html'
    paginate_by = 20
    filtering = (
        ('name',),
    )


class ViewInvestorAccount(ViewCarAccount, GlobalMainMenu):
    model = Investor


class ViewCashboxAccount(ViewCarAccount, GlobalMainMenu):
    model = CashBox


class ViewDriverAccount(ViewCarAccount, GlobalMainMenu):
    model = Driver


class ViewCounterpartAccount(ViewCarAccount, GlobalMainMenu):
    model = Counterpart


class ViewTaxiOperatorAccount(ViewCarAccount, GlobalMainMenu):
    model = TaxiOperator
