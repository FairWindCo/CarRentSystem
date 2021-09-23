from django.urls import path

from carmanagment.views import ViewTrips

urlpatterns = [
    path('test/', ViewTrips.as_view()),
]
