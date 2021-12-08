from django.db import models

from .custom_admin import ListAdmin
from carmanagment.models import Car


class MyList(ListAdmin):
    model_field_sets = {
        'name': models.CharField(max_length=250, verbose_name='Номерной знак'),
    }
    # model_query = Car
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    use_custom_view_template = True
    use_change_list = True

    def get_queryset(self, request):
        print('QUERYSET')
        return Car.objects.all()


def get_model_fields(model):
    fields = {}
    options = model._meta
    for field in sorted(options.concrete_fields):
        fields[field.name] = field
    return fields