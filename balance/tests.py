import datetime

from django.test import TestCase

# Create your tests here.
from balance.models import Account, AccountStatement, Transaction
from balance.services import Balance


class CheckBalance(TestCase):
    def setUp(self):
        self.test_account_1 = Account.objects.create(name='Test 1')
        self.test_account_2 = Account.objects.create(name='Test 2')
        self.test_account_3 = Account.objects.create(name='Test 3')
        self.test_account_4 = Account.objects.create(name='Test 4')
        self.transaction_type = Transaction.TransactionType.EXPENSE

    def test_balance_with_no_operation(self):
        self.assertEquals(Balance.get_current_balance(self.test_account_1), 0)
        self.assertEquals(Balance.get_current_balance(self.test_account_2), 0)
        self.assertEquals(Balance.get_current_balance(self.test_account_3), 0)
        self.assertEquals(Balance.get_current_balance(self.test_account_4), 0)

    def test_balance_operation(self):
        Balance.form_transaction(self.transaction_type, [
            (self.test_account_1, self.test_account_2, 50),
            (self.test_account_2, self.test_account_3, 150),
            (self.test_account_1, None, 50),
            (None, self.test_account_4, 50),
        ])
        self.assertEquals(Balance.get_current_balance(self.test_account_1), -100)
        self.assertEquals(Balance.get_current_balance(self.test_account_2), -100)
        self.assertEquals(Balance.get_current_balance(self.test_account_3), 150)
        self.assertEquals(Balance.get_current_balance(self.test_account_4), 50)

    def test_balance_operation_internal(self):
        transaction = Balance.form_transaction(self.transaction_type, [
            (self.test_account_1, self.test_account_2, 50),
            (self.test_account_2, self.test_account_3, 150),
            (self.test_account_1, None, 50),
            (None, self.test_account_4, 50),
        ])
        print(transaction.transactionTime)
        self.assertIsNotNone(transaction)
        set_operation = transaction.accounttransaction_set.all()
        self.assertTrue(len(set_operation) == 6)
        self.assertEquals(set_operation[0].amount, -50)
        self.assertEquals(set_operation[0].account, self.test_account_1)
        self.assertEquals(set_operation[1].amount, 50)
        self.assertEquals(set_operation[1].account, self.test_account_2)
        self.assertEquals(set_operation[2].amount, -150)
        self.assertEquals(set_operation[2].account, self.test_account_2)
        self.assertEquals(set_operation[3].amount, 150)
        self.assertEquals(set_operation[3].account, self.test_account_3)
        self.assertEquals(set_operation[4].amount, -50)
        self.assertEquals(set_operation[4].account, self.test_account_1)
        self.assertEquals(set_operation[5].amount, 50)
        self.assertEquals(set_operation[5].account, self.test_account_4)

    def test_account_statement_opearation(self):
        Balance.form_transaction(self.transaction_type, [
            (self.test_account_1, self.test_account_2, 50),
            (self.test_account_2, self.test_account_3, 150),
            (self.test_account_1, None, 50),
            (None, self.test_account_4, 50),
        ])

        balance, credit, debit = Balance.get_current_balance_totally(self.test_account_1)
        self.assertEquals(balance, -100)
        self.assertEquals(debit, 0)
        self.assertEquals(credit, 100)

        balance, credit, debit = Balance.get_current_balance_totally(self.test_account_2)
        self.assertEquals(balance, -100)
        self.assertEquals(debit, 50)
        self.assertEquals(credit, 150)

    def test_account_statement(self):
        transaction = Balance.form_transaction(self.transaction_type, [
            (self.test_account_1, self.test_account_2, 50),
            (self.test_account_2, self.test_account_3, 150),
            (self.test_account_1, None, 50),
            (None, self.test_account_4, 50),
        ])
        balance_date = (transaction.transactionTime + datetime.timedelta(days=1)).date()
        Balance.form_accounts_statements(on_date=balance_date)
        statement_set = AccountStatement.objects.order_by('account_id').all()
        self.assertTrue(len(statement_set) == 4)
        for statement in statement_set:
            self.assertEquals(statement.statementDate, balance_date)

        self.test_account_1.refresh_from_db()
        self.assertEquals(statement_set[0].closingBalance, -100)
        self.assertEquals(statement_set[0].totalCredit, 100)
        self.assertEquals(statement_set[0].totalDebit, 0)
        self.assertEquals(statement_set[0].account, self.test_account_1)
        self.assertEquals(statement_set[0], self.test_account_1.last_period_balance)

        self.test_account_2.refresh_from_db()
        self.assertEquals(statement_set[1].closingBalance, -100)
        self.assertEquals(statement_set[1].totalCredit, 150)
        self.assertEquals(statement_set[1].totalDebit, 50)
        self.assertEquals(statement_set[1].account, self.test_account_2)
        self.assertEquals(statement_set[1], self.test_account_2.last_period_balance)

        self.test_account_3.refresh_from_db()
        self.assertEquals(statement_set[2].closingBalance, 150)
        self.assertEquals(statement_set[2].totalCredit, 0)
        self.assertEquals(statement_set[2].totalDebit, 150)
        self.assertEquals(statement_set[2].account, self.test_account_3)
        self.assertEquals(statement_set[2], self.test_account_3.last_period_balance)

        self.test_account_4.refresh_from_db()
        self.assertEquals(statement_set[3].closingBalance, 50)
        self.assertEquals(statement_set[3].totalCredit, 0)
        self.assertEquals(statement_set[3].totalDebit, 50)
        self.assertEquals(statement_set[3].account, self.test_account_4)
        self.assertEquals(statement_set[3], self.test_account_4.last_period_balance)

    def test_account_statement_complex(self):
        fist_check = datetime.datetime(year=2021, month=8, day=1)
        transaction = Balance.form_transaction(self.transaction_type, [
            (self.test_account_1, self.test_account_2, 50),
            (self.test_account_2, self.test_account_3, 150),
            (self.test_account_1, None, 50),
            (None, self.test_account_4, 50),
        ])
        transaction.transactionTime = fist_check
        transaction.save()
        balance_date = (fist_check + datetime.timedelta(days=1)).date()
        Balance.form_accounts_statements(on_date=balance_date)
        statement_set = AccountStatement.objects.order_by('account_id').all()
        self.assertTrue(len(statement_set) == 4)
        for statement in statement_set:
            self.assertEquals(statement.statementDate, balance_date)

        self.test_account_1.refresh_from_db()
        self.assertEquals(statement_set[0].closingBalance, -100)
        self.assertEquals(statement_set[0].totalCredit, 100)
        self.assertEquals(statement_set[0].totalDebit, 0)
        self.assertEquals(statement_set[0].account, self.test_account_1)
        self.assertEquals(statement_set[0], self.test_account_1.last_period_balance)

        self.test_account_2.refresh_from_db()
        self.assertEquals(statement_set[1].closingBalance, -100)
        self.assertEquals(statement_set[1].totalCredit, 150)
        self.assertEquals(statement_set[1].totalDebit, 50)
        self.assertEquals(statement_set[1].account, self.test_account_2)
        self.assertEquals(statement_set[1], self.test_account_2.last_period_balance)

        self.test_account_3.refresh_from_db()
        self.assertEquals(statement_set[2].closingBalance, 150)
        self.assertEquals(statement_set[2].totalCredit, 0)
        self.assertEquals(statement_set[2].totalDebit, 150)
        self.assertEquals(statement_set[2].account, self.test_account_3)
        self.assertEquals(statement_set[2], self.test_account_3.last_period_balance)

        self.test_account_4.refresh_from_db()
        self.assertEquals(statement_set[3].closingBalance, 50)
        self.assertEquals(statement_set[3].totalCredit, 0)
        self.assertEquals(statement_set[3].totalDebit, 50)
        self.assertEquals(statement_set[3].account, self.test_account_4)
        self.assertEquals(statement_set[3], self.test_account_4.last_period_balance)

        transaction2 = Balance.form_transaction(self.transaction_type, [
            (None, self.test_account_1, 150),
            (self.test_account_3, self.test_account_2, 50),
            (self.test_account_1, None, 50),
            (None, self.test_account_4, 50),
        ])
        balance_date2 = (transaction2.transactionTime + datetime.timedelta(days=1)).date()
        Balance.form_accounts_statements(on_date=balance_date2)

        statement_set2 = AccountStatement.objects.order_by('account_id', 'statementDate').all()
        self.assertTrue(len(statement_set2) == 8)
        print(statement_set2)
        self.test_account_1.refresh_from_db()
        self.assertEquals(statement_set2[1].statementDate, balance_date2)
        self.assertEquals(statement_set2[1].account, self.test_account_1)
        self.assertEquals(statement_set2[1].closingBalance, Balance.get_current_balance(self.test_account_1))
        self.assertEquals(statement_set2[1].closingBalance, 0)
        self.assertEquals(statement_set2[1].totalCredit, 50)
        self.assertEquals(statement_set2[1].totalDebit, 150)
        self.assertEquals(statement_set2[1], self.test_account_1.last_period_balance)

        self.test_account_2.refresh_from_db()
        self.assertEquals(statement_set2[3].statementDate, balance_date2)
        self.assertEquals(statement_set2[3].closingBalance, -50)
        self.assertEquals(statement_set2[3].closingBalance, Balance.get_current_balance(self.test_account_2))
        self.assertEquals(statement_set2[3].totalCredit, 0)
        self.assertEquals(statement_set2[3].totalDebit, 50)
        self.assertEquals(statement_set2[3].account, self.test_account_2)
        self.assertEquals(statement_set2[3], self.test_account_2.last_period_balance)

        self.test_account_3.refresh_from_db()
        self.assertEquals(statement_set2[5].closingBalance, 100)
        self.assertEquals(statement_set2[5].closingBalance, Balance.get_current_balance(self.test_account_3))
        self.assertEquals(statement_set2[5].totalCredit, 50)
        self.assertEquals(statement_set2[5].totalDebit, 0)
        self.assertEquals(statement_set2[5].account, self.test_account_3)
        self.assertEquals(statement_set2[5], self.test_account_3.last_period_balance)
        self.assertEquals(statement_set2[5].statementDate, balance_date2)

        self.test_account_4.refresh_from_db()
        self.assertEquals(statement_set2[7].closingBalance, 100)
        self.assertEquals(statement_set2[7].closingBalance, Balance.get_current_balance(self.test_account_4))
        self.assertEquals(statement_set2[7].totalCredit, 0)
        self.assertEquals(statement_set2[7].totalDebit, 50)
        self.assertEquals(statement_set2[7].account, self.test_account_4)
        self.assertEquals(statement_set2[7], self.test_account_4.last_period_balance)
        self.assertEquals(statement_set2[7].statementDate, balance_date2)
