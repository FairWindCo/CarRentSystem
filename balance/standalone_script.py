import os
import sys
from balance.models import Account
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))

os.environ['DJANGO_SETTINGS_MODULE'] = 'CarRentSystem.settings'
django.setup()


if __name__ == '__main__':
    print(Account.objects.all())
