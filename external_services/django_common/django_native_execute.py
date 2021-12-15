import os
import sys

import django


def execute_code_in_django(execute_method):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.abspath(BASE_DIR))
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))
    print(BASE_DIR, os.path.abspath(os.path.join(BASE_DIR, os.pardir)))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'CarRentSystem.settings'

    django.setup()
    execute_method()
