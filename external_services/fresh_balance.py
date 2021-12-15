from datetime import timedelta
from django.utils import timezone

from .django_common.django_native_execute import execute_code_in_django


def refresh_balanses():
    from balance.models import Account

    current_date = timezone.now().date() - timedelta(days=1)
    for balance in Account.objects.all():
        current_statement_balance = balance.form_statement(current_date)
        print(balance.name, current_statement_balance)


if __name__ == '__main__':
    execute_code_in_django(lambda _: refresh_balanses())
