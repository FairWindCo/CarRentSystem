from datetime import date, datetime
from typing import Optional

from django.db import transaction
from django.db.models import Sum
from django.utils.timezone import now

from balance.models import Account, AccountTransaction, AccountStatement, Transaction


class Balance:
    EXPENSE = Transaction.TransactionType.EXPENSE
    RECEIPT = Transaction.TransactionType.RECEIPT
    TRANSFER = Transaction.TransactionType.TRANSFER
    DEPOSIT = Transaction.TransactionType.DEPOSIT
    WITHDRAWAL = Transaction.TransactionType.WITHDRAWAL
    INVESTMENT = Transaction.TransactionType.INVESTMENT

    @staticmethod
    # Create one transaction with list of account operation (from_account, to_account, amount)
    def form_transaction(transaction_type: Transaction.TransactionType,
                         operations: list[tuple[Account, Account, int]],
                         ) -> Optional[Transaction]:
        with transaction.atomic():
            transaction_obj = Transaction()
            transaction_obj.transactionType = transaction_type
            if operations:
                transaction_obj.save()
                for operation in operations:
                    if operation[0] is not None:
                        operation_left = AccountTransaction(transaction=transaction_obj,
                                                            account=operation[0],
                                                            amount=-operation[2])
                        operation_left.save()
                    if operation[1] is not None:
                        operation_right = AccountTransaction(transaction=transaction_obj,
                                                             account=operation[1],
                                                             amount=operation[2])
                        operation_right.save()
                return transaction_obj
        return None

    @staticmethod
    # create statement on date for all accounts
    def form_accounts_statements(on_date=None):
        if on_date is None:
            on_date = now()
        if isinstance(on_date, datetime):
            on_date = on_date.date()
        with transaction.atomic():
            for account in Account.objects.all():
                balance, total_credit, total_debit = Balance.get_current_balance_totally(account, on_date)
                account_statement = AccountStatement(statementDate=on_date, account=account,
                                                     closingBalance=balance, totalCredit=total_credit,
                                                     totalDebit=total_debit)
                account_statement.save()
                account.last_period_balance = account_statement
                account.save()

    @staticmethod
    # return last statement balance for account on date
    def get_statement_balance(account: Account, on_date: date) -> \
            tuple[int, Optional[date], Optional[AccountStatement]]:
        if on_date is None:
            on_date = now().date()
        else:
            if isinstance(on_date, datetime):
                on_date = on_date.date()
        if account.last_period_balance is not None and account.last_period_balance.statementDate <= on_date:
            last_balance = account.last_period_balance
        else:
            last_balance = AccountStatement.objects.filter(account=account, statementDate__lte=on_date).order_by(
                '-statementDate').first()

        if last_balance is None:
            return 0, None, None
        return last_balance.closingBalance, last_balance.statementDate, last_balance

    @staticmethod
    # get balance for account on date
    def get_current_balance(account: Account, on_date=None) -> int:
        balance = 0
        if account:
            if on_date is None:
                on_date = now()
            balance, from_date, _ = Balance.get_statement_balance(account, on_date)
            if from_date is not None:
                total = AccountTransaction.objects.filter(account=account,
                                                          transaction__transactionTime__gt=from_date,
                                                          transaction__transactionTime__lte=on_date).aggregate(
                    Sum('amount'))
                balance = balance + total['amount__sum']
            else:
                balance = AccountTransaction.objects.filter(account=account,
                                                            transaction__transactionTime__lte=on_date).aggregate(
                    Sum('amount'))['amount__sum']
        return 0 if balance is None else balance

    @staticmethod
    # return balance, totalCredit, totalDebit
    def get_current_balance_totally(account: Account, on_date=None) -> tuple[int, int, int]:
        balance = 0
        total_credit = 0
        total_debit = 0

        if account:
            if on_date is None:
                on_date = now()
            balance, from_date, last_balance = Balance.get_statement_balance(account, on_date)
            if from_date is not None:
                total = AccountTransaction.objects.filter(account=account,
                                                          transaction__transactionTime__gt=from_date,
                                                          transaction__transactionTime__lte=on_date).aggregate(
                    Sum('amount'))
                total_credit = AccountTransaction.objects.filter(account=account, amount__lt=0,
                                                                 transaction__transactionTime__gt=from_date,
                                                                 transaction__transactionTime__lte=on_date).aggregate(
                    Sum('amount'))['amount__sum']
                total_debit = AccountTransaction.objects.filter(account=account, amount__gt=0,
                                                                transaction__transactionTime__gt=from_date,
                                                                transaction__transactionTime__lte=on_date).aggregate(
                    Sum('amount'))['amount__sum']
                if total['amount__sum'] is not None:
                    balance = balance + total['amount__sum']
            else:
                balance = AccountTransaction.objects.filter(account=account,
                                                            transaction__transactionTime__lte=on_date).aggregate(
                    Sum('amount'))['amount__sum']
                total_credit = AccountTransaction.objects.filter(account=account, amount__lt=0,
                                                                 transaction__transactionTime__lte=on_date).aggregate(
                    Sum('amount'))['amount__sum']
                total_debit = AccountTransaction.objects.filter(account=account, amount__gt=0,
                                                                transaction__transactionTime__lte=on_date).aggregate(
                    Sum('amount'))['amount__sum']
        balance = 0 if balance is None else balance
        total_credit = 0 if total_credit is None else -total_credit
        total_debit = 0 if total_debit is None else total_debit
        return balance, total_credit, total_debit
