from django.db import transaction

from balance.models import Account
from balance.services import Balance


class AccountService:
    @staticmethod
    def transfer_money(credit: Account, debit: Account, amount: float, description:str):
        if credit and debit and amount > 0:
            with transaction.atomic():
                transaction_record = Balance.form_transaction(Balance.EXPENSE, [
                    (credit, debit, round(amount * 100), ''),
                ], description)
                return True, transaction_record
        return False, None