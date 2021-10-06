from django.urls import path

from carmanagment.views import ViewTrips, ViewTripsNew, ViewTripsNew2

urlpatterns = [
    path('test/', ViewTrips.as_view()),
    path('json/', ViewTripsNew.as_view()),
    path('json2/', ViewTripsNew2.as_view()),

]
