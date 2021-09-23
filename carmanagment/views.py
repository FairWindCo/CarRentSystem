from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView
from vue_utils.views import FilterListView

from carmanagment.models import TaxiTrip


class ViewTrips(FilterListView):
    model = TaxiTrip
    template_name = 'carmanagment/trip_list.html'
