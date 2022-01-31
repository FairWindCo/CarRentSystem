from django.urls import path

from car_management.views import ViewCarExpenses, OperationsView, \
    TransactionView, ViewCarAccount, ViewInvestorAccount, ViewDriverAccount, ViewTaxiOperatorAccount, \
    ViewCounterpartAccount, ViewCarInvestmentAccount, test_view, dashboard, \
    ViewCashboxAccount
from trips.views.viewtrips import ViewCarWialons, ViewCarWialonsStat

urlpatterns = [
    path('cars', ViewCarAccount.as_view(), name='cars'),
    path('drivers', ViewDriverAccount.as_view(), name='drivers'),
    path('investors', ViewInvestorAccount.as_view(), name='investors'),
    path('taxi_operators', ViewTaxiOperatorAccount.as_view(), name='taxi_operators'),
    path('counterparts', ViewCounterpartAccount.as_view(), name='counterparts'),
    path('invest', ViewCarInvestmentAccount.as_view(), name='invest'),
    path('cashbox', ViewCashboxAccount.as_view(), name='cashbox'),



    path('car_wialon_trip/<car_name>/', ViewCarWialons.as_view(), name='wialon_trips_by_car'),
    path('car_wialon_trip', ViewCarWialons.as_view(), name='all_wialon_trips'),
    path('car_wialon_stat/<car_name>/', ViewCarWialonsStat.as_view(), name='wialon_stat_by_car'),
    path('car_wialon_stat', ViewCarWialonsStat.as_view(), name='all_wialon_stat'),
    path('car_expenses', ViewCarExpenses.as_view(), name='all_expenses'),
    path('car_expenses/<car_name>/', ViewCarExpenses.as_view(), name='expenses_by_car'),
    path('operations', OperationsView.as_view(), name='all_operations'),
    path('transactions', TransactionView.as_view(), name='all_transactions'),
    path('dashboard', dashboard, name='dashboard'),

    path('test_view', test_view),


]
