from balance.models import CashBox
from car_management.models import Car, Investor, Driver, Counterpart
from car_management.views.global_menu import GlobalMainMenu
from car_rent.models import TaxiOperator
from django_helpers.django_request_processor import UniversalFilterListView


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
