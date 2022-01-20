
from comlex_data_pump import uklon_data_pump
from django_common.django_native_execute import execute_code_in_django
from external_services.argument_parser import current_date

if __name__ == '__main__':
    execute_code_in_django(lambda:uklon_data_pump(
        current_date(),
        6,
        cache_path='UKLON'
    ))
