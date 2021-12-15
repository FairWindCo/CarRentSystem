import datetime
import os.path

from external_services.comlex_data_pump import uklon_data_pump
from external_services.django_common.django_native_execute import execute_code_in_django

if __name__ == '__main__':

    execute_code_in_django(lambda: uklon_data_pump(
        datetime.datetime.strptime('11.12.2021', '%d.%m.%Y'),
        7,
        os.path.join(os.path.curdir, 'UKLON')
    ))
