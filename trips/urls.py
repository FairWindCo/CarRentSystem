from django.urls import path

from trips.views.viewtrips import ViewCarWialons, ViewCarWialonsStat, ViewTrips, ViewTripsNew, ViewTripsNew2, \
    ViewCarTrips
from trips.views.carview import TripStatistics, CarSummaryStatistics, ViewCarStatistic, ByCarView

urlpatterns = [
    path('car_trip', ViewCarTrips.as_view(), name='all_trips'),
    path('car_wialon_trip/<car_name>/', ViewCarWialons.as_view(), name='wialon_trips_by_car'),
    path('car_wialon_trip', ViewCarWialons.as_view(), name='all_wialon_trips'),
    path('car_wialon_stat/<car_name>/', ViewCarWialonsStat.as_view(), name='wialon_stat_by_car'),
    path('car_wialon_stat', ViewCarWialonsStat.as_view(), name='all_wialon_stat'),
    path('car_trip/<car_name>/', ViewCarTrips.as_view(), name='trip_by_car'),
    path('car_stat', ViewCarStatistic.as_view(), name='trip_stat'),
    path('car_stat/<car_name>/', ViewCarStatistic.as_view(), name='trip_stat_by_car'),

    path('test/', ViewTrips.as_view()),
    path('json/', ViewTripsNew.as_view()),
    path('json2/', ViewTripsNew2.as_view()),

]
