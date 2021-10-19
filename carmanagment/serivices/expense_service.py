import math

from django.db import transaction

from balance.models import Account
from balance.services import Balance
from carmanagment.models import ExpensesTypes, Counterpart, Expenses, Car


class ExpensesProcessor:
    @staticmethod
    def form_expense(account: Account,
                     amount: float,
                     expense_type: ExpensesTypes,
                     counterpart: Counterpart,
                     description: str) -> Expenses:
        if expense_type.type_class in [ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE,
                                       ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE,
                                       ]:
            raise TypeError('TypeError class may be not CAR_EXPENSE and not CAPITAL_CAR_EXPENSE')
        if isinstance(account, Car) or account.car is not None:
            raise TypeError('car account not allowed')
        if account.currency == Account.AccountCurrency.DOLLAR:
            raise TypeError('Investment balance is not allowed')
        with transaction.atomic():
            transaction_record = Balance.form_transaction(Balance.EXPENSE,
                                                          [
                                                              (
                                                                  account,
                                                                  counterpart,
                                                                  math.trunc(amount * 100),
                                                                  'Эатрата'
                                                              ),
                                                          ],
                                                          description
                                                          )
            expense = Expenses(
                account=account, counterpart=counterpart, expenseType=expense_type,
                description=description, transaction=transaction_record, amount=amount
            )
            expense.save()
            return expense

    @staticmethod
    def form_car_current_expense(car: Car,
                                 amount: float,
                                 expense_type: ExpensesTypes,
                                 counterpart: Counterpart,
                                 description: str) -> Expenses:
        if expense_type.type_class != ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE:
            raise TypeError('TypeError class only CAR_EXPENSE')
        with transaction.atomic():
            transaction_record = Balance.form_transaction(Balance.EXPENSE,
                                                          [
                                                              (
                                                                  car,
                                                                  counterpart,
                                                                  math.trunc(amount * 100),
                                                                  'Расходы на машину'
                                                              )
                                                          ], description
                                                          )
            expense = Expenses(
                account=car, counterpart=counterpart, expenseType=expense_type,
                description=description, transaction=transaction_record
            )
            expense.save()
            return expense

    @staticmethod
    def form_car_capital_expense(car: Car,
                                 amount: float, course: float,
                                 expense_type: ExpensesTypes,
                                 counterpart: Counterpart,
                                 description: str) -> Expenses:
        if expense_type.type_class != ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE:
            raise TypeError('TypeError class only CAPITAL_CAR_EXPENSE')
        with transaction.atomic():
            transaction_record = Balance.form_transaction(Balance.EXPENSE, [
                (car, counterpart, math.trunc(amount * 100), 'Затрата на автомобиль'),
                (car.car_investor, car, math.trunc(amount * 100), 'Капитальная затрата'),
                (car.investment, None, math.trunc(amount * 100 / course), 'Увеличения стоимости капитала')
            ], description)
            expense = Expenses(
                account=car, counterpart=counterpart, expenseType=expense_type,
                description=description, transaction=transaction_record,
                amount=amount
            )
            expense.save()
            return expense