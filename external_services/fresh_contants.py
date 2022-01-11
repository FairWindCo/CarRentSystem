import datetime

from comlex_data_pump import uklon_data_pump
from django_common.django_native_execute import execute_code_in_django

if __name__ == '__main__':
    execute_code_in_django(lambda:uklon_data_pump(
        datetime.date.today(),
        1
    ))
