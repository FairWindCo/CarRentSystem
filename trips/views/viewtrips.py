from vue_utils.views import FilterListView

from trips.models.taxi import TaxiTrip
from trips.models.wialon import WialonTrip, WialonDayStat
from trips.views.carview import ByCarView
from car_management.views.global_menu import GlobalMainMenu
from django_helpers.django_request_processor import UniversalFilterListView


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


class ViewCarWialons(UniversalFilterListView, ByCarView, GlobalMainMenu):
    model = WialonTrip
    template_name = 'carmanagment/cars_wialon_list.html'
    paginate_by = 20
    ordering = ('-start',)
    filtering = (
        ('car__name',),
        ('start__gte', 'start_interval'),
        ('end__lte', 'end_interval'),
    )

    def get_queryset(self):
        if self.current_car:
            self.queryset = WialonTrip.objects.filter(car=self.current_car).all()
        return super().get_queryset()


class ViewCarWialonsStat(UniversalFilterListView, ByCarView, GlobalMainMenu):
    model = WialonDayStat
    template_name = 'carmanagment/cars_wialon_stat_list.html'
    paginate_by = 20
    ordering = ('-stat_date',)
    filtering = (
        ('car__name',),
        ('stat_date__gte', 'start_interval'),
        ('stat_date__lte', 'end_interval'),
    )

    def get_queryset(self):
        if self.current_car:
            self.queryset = WialonDayStat.objects.filter(car=self.current_car, stat_interval=86400).all()
        return super().get_queryset()
