from django.urls import path

from carmanagment.views import ViewTrips, ViewTripsNew, ViewTripsNew2, ViewCarTrips, ViewCarExpenses, OperationsView, \
    TransactionView, ViewCarAccount, ViewInvestorAccount, ViewDriverAccount, ViewTaxiOperatorAccount, \
    ViewCounterpartAccount, ViewCarInvestmentAccount, test_view, ViewCarStatistic, dashboard, car_usage_report, \
    ViewCashboxAccount

urlpatterns = [
    path('cars', ViewCarAccount.as_view(), name='cars'),
    path('drivers', ViewDriverAccount.as_view(), name='drivers'),
    path('investors', ViewInvestorAccount.as_view(), name='investors'),
    path('taxi_operators', ViewTaxiOperatorAccount.as_view(), name='taxi_operators'),
    path('counterparts', ViewCounterpartAccount.as_view(), name='counterparts'),
    path('invest', ViewCarInvestmentAccount.as_view(), name='invest'),
    path('cashbox', ViewCashboxAccount.as_view(), name='cashbox'),



    path('car_trip', ViewCarTrips.as_view(), name='all_trips'),
    path('car_trip/<car_name>/', ViewCarTrips.as_view(), name='trip_by_car'),
    path('car_expenses', ViewCarExpenses.as_view(), name='all_expenses'),
    path('car_expenses/<car_name>/', ViewCarExpenses.as_view(), name='expenses_by_car'),
    path('operations', OperationsView.as_view(), name='all_operations'),
    path('transactions', TransactionView.as_view(), name='all_transactions'),
    path('car_stat', ViewCarStatistic.as_view(), name='trip_stat'),
    path('car_stat/<car_name>/', ViewCarStatistic.as_view(), name='trip_stat_by_car'),
    path('dashboard', dashboard, name='dashboard'),
    path('car_report', car_usage_report, name='car_report'),


    path('test/', ViewTrips.as_view()),
    path('json/', ViewTripsNew.as_view()),
    path('json2/', ViewTripsNew2.as_view()),
    path('test_view', test_view),


]
