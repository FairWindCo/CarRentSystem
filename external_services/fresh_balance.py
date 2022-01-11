from datetime import timedelta
from django.utils import timezone

from comlex_data_pump import parse_args
from django_common.django_native_execute import execute_code_in_django


def refresh_balanses(current_date=timezone.now().date() - timedelta(days=1)):
    from balance.models import Account

    for balance in Account.objects.all():
        current_statement_balance = balance.form_statement(current_date)
        print(balance.name, current_statement_balance)


if __name__ == '__main__':
    start_date, _, _ = parse_args('Get car data from Uklon')
    execute_code_in_django(lambda _: refresh_balanses(start_date))
