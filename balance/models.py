from django.db import models


# Create your models here.
class Account(models.Model):
    name = models.CharField(max_length=250)
    last_period_balance = models.ForeignKey('AccountStatement', null=True, on_delete=models.SET_NULL)


class AccountStatement(models.Model):
    statementDate = models.DateField(auto_now=True, auto_created=True, auto_now_add=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    closingBalance = models.BigIntegerField()
    totalCredit = models.BigIntegerField()
    totalDebit = models.BigIntegerField()


class TransactionType(models.Model):
    name = models.CharField(max_length=255)


class Transaction(models.Model):
    transactionTime = models.DateTimeField(auto_created=True, auto_now_add=True)
    transactionType = models.ForeignKey(TransactionType, on_delete=models.SET_NULL)


class AccountTransaction(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.PositiveBigIntegerField()
