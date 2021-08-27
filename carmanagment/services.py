import math

from django.db import transaction
from django.utils.timezone import now

from balance.services import Balance
from carmanagment.models import Expenses, ExpensesTypes, Counterpart, Car, CarModel, InvestmentCarBalance, Investor


class CarCreator:
    @staticmethod
    def add_new_car(investor: Investor, model: CarModel, car_plate: str, year: int, mileage_at_start: int,
                    start_amount: int) -> Car:
        car = Car(name=car_plate, year=year, mileage_at_start=mileage_at_start, control_mileage=mileage_at_start,
                  model=model, car_investor=investor)
        car.investment = InvestmentCarBalance(name=car_plate, create_date=now().date())
        car.investment.save()
        car.save()
        Balance.form_transaction(Balance.DEPOSIT, [(car.investment, None, start_amount)])
        return car


class CarExpensesProcessor:
    @staticmethod
    def form_car_current_expense(car: Car,
                                 amount: int,
                                 expense_type: ExpensesTypes,
                                 counterpart: Counterpart,
                                 description: str) -> Expenses:
        with transaction.atomic():
            transaction_record = Balance.form_transaction(Balance.EXPENSE, [(car, counterpart, amount)])
            expense = Expenses(
                account=car, counterpart=counterpart, expenseType=expense_type,
                description=description, transaction=transaction_record
            )
            expense.save()
            return expense

    @staticmethod
    def form_car_capital_expense(car: Car,
                                 amount: int, course: float,
                                 expense_type: ExpensesTypes,
                                 counterpart: Counterpart,
                                 description: str) -> Expenses:
        with transaction.atomic():
            transaction_record = Balance.form_transaction(Balance.EXPENSE, [
                (car, counterpart, amount),
                (car.car_investor, car, amount),
                (car.investment, None, math.trunc(amount / course))
            ])
            expense = Expenses(
                account=car, counterpart=counterpart, expenseType=expense_type,
                description=description, transaction=transaction_record,
                amount=amount
            )
            expense.save()
            return expense
