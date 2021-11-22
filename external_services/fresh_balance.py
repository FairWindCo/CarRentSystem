import os
import sys
from datetime import timedelta

import django
from django.utils import timezone


def refresh_balanses():
    from balance.models import Account

    current_date = timezone.now().date() - timedelta(days=1)
    for balance in Account.objects.all():
        current_statement_balance = balance.form_statement(current_date)
        print(balance.name, current_statement_balance)


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.abspath(BASE_DIR))
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))

    os.environ['DJANGO_SETTINGS_MODULE'] = 'CarRentSystem.settings'

    django.setup()
    refresh_balanses()
