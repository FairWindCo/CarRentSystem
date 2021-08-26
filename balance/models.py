from django.db import models


# Create your models here.
class Account(models.Model):
    name = models.CharField(max_length=250)
    last_period_balance = models.ForeignKey('AccountStatement', null=True, on_delete=models.SET_NULL,
                                            related_name='for_account')


class AccountStatement(models.Model):
    statementDate = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    closingBalance = models.BigIntegerField()
    totalCredit = models.BigIntegerField()
    totalDebit = models.BigIntegerField()

    def __str__(self):
        return f'S[{self.statementDate.strftime("%Y.%m.%d")}:{self.account.name}] = {self.closingBalance},{self.totalDebit},{self.totalCredit}'


class TransactionType(models.Model):
    name = models.CharField(max_length=255)


class Transaction(models.Model):
    transactionTime = models.DateTimeField(auto_now_add=True)
    transactionType = models.ForeignKey(TransactionType, on_delete=models.PROTECT)


class AccountTransaction(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.BigIntegerField()

    def __str__(self):
        return f'T[{self.transaction.id}] {self.account.name} {self.amount}'
