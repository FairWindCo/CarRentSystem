import os
import sys

import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))

os.environ['DJANGO_SETTINGS_MODULE'] = 'CarRentSystem.settings'
django.setup()

from balance.models import Account

if __name__ == '__main__':
    print(Account.objects.all())
