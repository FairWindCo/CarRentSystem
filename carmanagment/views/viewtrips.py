from vue_utils.views import FilterListView

from carmanagment.models import TaxiTrip
from carmanagment.views.carview import ByCarView
from carmanagment.views.global_menu import GlobalMainMenu
from django_request_processor.django_list_view import UniversalFilterListView


class ViewTrips(FilterListView):
    model = TaxiTrip
    template_name = 'carmanagment/trip_list.html'
    paginate_by = 20
    filters_fields = (
        ('car__name', 'icontains', None, None, False, False),
        ('timestamp__gte', None, 'start_interval'),
        ('timestamp__lte', None, 'end_interval'),
    )


class ViewTripsNew(UniversalFilterListView, GlobalMainMenu):
    model = TaxiTrip
    template_name = 'carmanagment/trip_list.html'
    paginate_by = 20
    use_custom_order = True
    return_json_as_response = True
    serialize = (
        ('timestamp', None, 'str_datetime_%d.%m.%Y %H:%M:%S', 'special'),
    )
    filtering = (
        ('car__name',),
        ('timestamp__gte', 'start_interval'),
        ('timestamp__lte', 'end_interval'),
    )


class ViewTripsNew2(UniversalFilterListView, GlobalMainMenu):
    model = TaxiTrip
    template_name = 'carmanagment/trip_list.html'
    use_custom_paging = False
    paginate_by = 20
    filters = (
        ('car__name',),
        ('timestamp__gte', 'start_interval'),
        ('timestamp__lte', 'end_interval'),
    )


class ViewCarTrips(UniversalFilterListView, ByCarView, GlobalMainMenu):
    model = TaxiTrip
    template_name = 'carmanagment/cars_trip_list.html'
    paginate_by = 20
    ordering = ('-timestamp',)
    filtering = (
        ('car__name',),
        ('timestamp__gte', 'start_interval'),
        ('timestamp__lte', 'end_interval'),
    )

    def get_queryset(self):
        if self.current_car:
            self.queryset = TaxiTrip.objects.filter(car=self.current_car).all()
        return super().get_queryset()