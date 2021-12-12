from datetime import datetime, date

from django.db import models
# Create your models here.
from django.db.models import Sum
from django.utils.timezone import now


class Account(models.Model):
    class AccountCurrency(models.IntegerChoices):
        GRIVNA = 0, 'грн'
        DOLLAR = 1, '$'

    name = models.CharField(max_length=250, verbose_name='имя/название/гос номер')
    last_period_balance = models.ForeignKey('AccountStatement', null=True, on_delete=models.SET_NULL,
                                            related_name='for_account', blank=True,
                                            verbose_name='Последний зафиксированный баланс'
                                            )
    currency = models.PositiveSmallIntegerField(choices=AccountCurrency.choices, default=AccountCurrency.GRIVNA,
                                                verbose_name='валюта')

    def __str__(self):
        account_str = f'{self.last_period_balance.closingBalance} ' \
                      f'{self.last_period_balance.statementDate.strftime("%d.%m.%Y")}' \
            if self.last_period_balance else '--'
        return f'{self.name} ({account_str}){self.get_currency()}'

    class Meta:
        verbose_name = 'Баланс'
        verbose_name_plural = 'Балансы'
        ordering = ('name',)

    def get_currency(self):
        return Account.AccountCurrency.labels[self.currency]

    # return last statement balance for account on date
    def get_statement_balance(self, on_date: date):
        if on_date is None:
            on_date = now().date()
        else:
            if isinstance(on_date, datetime):
                on_date = on_date.date()
        if self.last_period_balance is not None and self.last_period_balance.statementDate <= on_date:
            last_balance = self.last_period_balance
        else:
            last_balance = AccountStatement.objects.filter(account_id=self.pk, statementDate__lte=on_date).order_by(
                '-statementDate').first()

        if last_balance is None:
            return 0, None, None
        return last_balance.closingBalance, last_balance.statementDate, last_balance

    def get_current_balance(self, on_date=None) -> int:

        if on_date is None:
            on_date = now()
        balance, from_date, _ = self.get_statement_balance(on_date)
        if from_date is not None:
            total = AccountTransaction.objects.filter(account=self,
                                                      transaction__transactionTime__gt=from_date,
                                                      transaction__transactionTime__lte=on_date).aggregate(
                Sum('amount'))['amount__sum']
            balance = balance + (total if total is not None else 0)
        else:
            balance = AccountTransaction.objects.filter(account=self,
                                                        transaction__transactionTime__lte=on_date).aggregate(
                Sum('amount'))['amount__sum']
            balance = balance if balance is not None else 0
        return balance

    def form_statement(self, on_date=None):
        if on_date is None:
            on_date = now()
        old_balance, from_date, statement_balance = self.get_statement_balance(on_date)
        if statement_balance:
            return statement_balance
        if from_date is not None:
            credit = AccountTransaction.objects.filter(account=self, amount__lt=0,
                                                       transaction__transactionTime__gt=from_date,
                                                       transaction__transactionTime__lte=on_date).aggregate(
                Sum('amount'))['amount__sum']
            debit = AccountTransaction.objects.filter(account=self, amount__gt=0,
                                                      transaction__transactionTime__gt=from_date,
                                                      transaction__transactionTime__lte=on_date).aggregate(
                Sum('amount'))['amount__sum']
        else:
            old_balance = 0
            credit = AccountTransaction.objects.filter(account=self, amount__lt=0,
                                                       transaction__transactionTime__lte=on_date).aggregate(
                Sum('amount'))['amount__sum']
            debit = AccountTransaction.objects.filter(account=self, amount__gt=0,
                                                      transaction__transactionTime__lte=on_date).aggregate(
                Sum('amount'))['amount__sum']
        debit = int(0 if debit is None else debit)
        credit = int(0 if credit is None else credit)
        balance = old_balance + debit + credit

        statement_balance = AccountStatement(account=self, statementDate=on_date, closingBalance=balance,
                                             totalDebit=debit, totalCredit=credit)
        statement_balance.save()
        no_update = AccountStatement.objects.filter(account=self, statementDate__gt=on_date).exists()
        if not no_update:
            self.last_period_balance = statement_balance
            self.save()
        return statement_balance

    def current_balance(self):
        balance = self.get_current_balance()
        return balance / 100 if balance else 0

    def last_statemnet_balance(self):
        if self.last_period_balance:
            return self.last_period_balance.closingBalance / 100
        else:
            return 0

    def last_statemnet_debit(self):
        if self.last_period_balance:
            return self.last_period_balance.totalDebit / 100
        else:
            return 0

    def last_statemnet_credit(self):
        if self.last_period_balance:
            return self.last_period_balance.totalCredit / 100
        else:
            return 0

    def last_statemnet_date(self):
        if self.last_period_balance:
            return self.last_period_balance.statementDate.strftime('%d.%m.%Y')
        else:
            return '---'


class AccountStatement(models.Model):
    statementDate = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    closingBalance = models.BigIntegerField()
    totalCredit = models.BigIntegerField()
    totalDebit = models.BigIntegerField()

    def __str__(self):
        return f'S[{self.statementDate.strftime("%Y.%m.%d")}:' \
               f'{self.account.name}] = {self.closingBalance},{self.totalDebit},{self.totalCredit} ' \
               f'{Account.AccountCurrency.labels[self.account.currency]}'

    class Meta:
        verbose_name = 'Состояния баланса за дату'
        verbose_name_plural = 'Переодические состояния балансов'
        ordering = ('account', 'statementDate')
        unique_together = ('account', 'statementDate')


class Transaction(models.Model):
    class TransactionType(models.IntegerChoices):
        EXPENSE = 0, 'Расход'
        RECEIPT = 1, 'Приход'
        TRANSFER = 3, 'Перевод средств между счетами'
        DEPOSIT = 4, 'Внесение денежных средств '
        WITHDRAWAL = 5, 'Вывод денежных средств'
        INVESTMENT = 6, 'Инвестиция'
        INSURANCE = 7, 'Строховка'

    transactionTime = models.DateTimeField(auto_now_add=True, verbose_name='Время транзакции')
    transactionType = models.IntegerField(choices=TransactionType.choices, verbose_name='Тип')
    comment = models.TextField(max_length=1000, default='', blank=True, null=True)

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'транзакции'

    def get_transaction_type(self):
        for el in Transaction.TransactionType.choices:
            if el[0] == self.transactionType:
                return el[1]
        return '--'

    def __str__(self):
        return f'{self.pk} [{self.transactionTime.strftime("%d.%m.%Y %H:%M:%S")}] - {self.get_transaction_type()}'


class AccountTransaction(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.BigIntegerField()
    comment = models.CharField(max_length=100, default='', blank=True, null=True)

    def __str__(self):
        return f'T[{self.transaction.id}] {self.account.name} {self.amount}{Account.AccountCurrency.labels[self.account.currency]}'

    class Meta:
        verbose_name = 'Операция в транзакция'
        verbose_name_plural = 'Транзакционные операции'


    def cents_amount(self):
        return f'{self.amount / 100:.2f}'


class CashBox(Account):
    class Meta:
        verbose_name = 'Касса'
        verbose_name_plural = 'Кассы'

    def __str__(self):
        cash = self.get_current_balance()
        cash = cash/100 if cash else 0
        return f'{self.name} {cash:.2f}{self.get_currency()}'