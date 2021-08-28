from ajax_select import register, LookupChannel
from django.db.models import Q

from carmanagment.models import CarModel


@register('car_models')
class ModelLookup(LookupChannel):
    model = CarModel

    def get_query(self, q, request):
        return self.model.objects.filter(Q(name__icontains=q)|(Q(brand__name__icontains=q))).order_by('name')[:50]

    def format_item_display(self, item):
        return f"<span class='car_model'>{item.brand.name} {item.name}</span>"
