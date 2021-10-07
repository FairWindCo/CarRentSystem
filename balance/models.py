from django.db import models


# Create your models here.
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

    transactionTime = models.DateTimeField(auto_now_add=True, verbose_name='Время транзакции')
    transactionType = models.IntegerField(choices=TransactionType.choices, verbose_name='Тип')
    comment = models.TextField(max_length=1000, default='', blank=True, null=True)

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'транзакции'

    def get_transaction_type(self):
        return Transaction.TransactionType.labels[self.transactionType]

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
        return f'{self.amount/100:.2f}'
