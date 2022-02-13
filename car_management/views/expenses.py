from django.contrib.auth.mixins import LoginRequiredMixin

from car_management.models import Expenses, Car
from trips.views.carview import ByCarView
from car_management.views.global_menu import GlobalMainMenu
from django_helpers.django_request_processor import UniversalFilterListView


class ViewCarExpenses(UniversalFilterListView, ByCarView, GlobalMainMenu):
    model = Expenses
    template_name = 'carmanagment/cars_expenses_list.html'
    paginate_by = 20
    ordering = ('-date_mark',)
    filtering = (
        ('account__name__icontains', 'name'),
        ('date_mark__gte', 'start_interval'),
        ('date_mark__lte', 'end_interval'),
    )

    def get_queryset(self):
        if self.current_car:
            self.queryset = Expenses.objects.filter(account=self.current_car)
        else:
            self.queryset = Expenses.objects.filter(account__pk__in=Car.objects.values('pk').all())
        return super().get_queryset()