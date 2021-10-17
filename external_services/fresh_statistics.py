import datetime
import os
import sys

import django



if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))

    os.environ['DJANGO_SETTINGS_MODULE'] = 'CarRentSystem.settings'

    django.setup()
    from carmanagment.services import Statistics
    Statistics.create_statistics(datetime.datetime.strptime('21.09.2021','%d.%m.%Y'))
