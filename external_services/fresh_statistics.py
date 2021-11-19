import datetime
import os
import sys

import django



if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.abspath(BASE_DIR)) 
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))

    os.environ['DJANGO_SETTINGS_MODULE'] = 'CarRentSystem.settings'

    django.setup()
    from carmanagment.serivices.statisrics_service import Statistics

    Statistics.create_statistics((datetime.datetime.now().date() - datetime.timedelta(days=1)))
#    Statistics.create_statistics(datetime.datetime.strptime('16.10.2021', '%d.%m.%Y'))
