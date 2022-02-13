import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from car_management.views.global_menu import GlobalMainMenu
from trip_stat.services.statisrics_service import Statistics


@login_required
def dashboard(request):
    import random

    def getRandomCol():

        r = hex(random.randrange(0, 16))[2:] + hex(random.randrange(0, 16))[2:]
        g = hex(random.randrange(0, 255))[2:] + hex(random.randrange(0, 16))[2:]
        b = hex(random.randrange(0, 255))[2:] + hex(random.randrange(0, 16))[2:]

        random_col = '#' + r[:2] + g[:2] + b[:2]
        return random_col

    context = GlobalMainMenu.form_menu_context(request)
    trip_stat = Statistics.get_last_statistics()
    context['page_header'] = 'DashBoard'
    trip_data = []
    trip_sum = []
    trip_label = []
    trip_color = []
    for index, (name, stats) in enumerate(trip_stat.items()):
        trip_data.append(
            {'name': name,
             'data': [el.trip_count for el in stats]})
        trip_sum.append(
            {'name': name,
             'data': [el.amount for el in stats]})
        trip_color.append(getRandomCol())
        if index == 0:
            trip_label = [el.stat_date.strftime('%d.%m.%y') for el in stats]

    context['trips_data'] = trip_data
    context['trips_sum'] = trip_sum
    context['cars'] = json.dumps(trip_label)
    context['colors'] = json.dumps(trip_color)
    return render(request, 'admin_template/dashboard.html', context)
