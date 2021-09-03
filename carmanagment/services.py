import math

from django.db import transaction
from django.utils.datetime_safe import datetime
from django.utils.timezone import now

from balance.models import Account
from balance.services import Balance
from carmanagment.models import Expenses, ExpensesTypes, Counterpart, Car, CarModel, InvestmentCarBalance, Investor, \
    TaxiTrip, Driver


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

    @staticmethod
    def add_new_car_from_id(investor_id: int, model_id: int, car_plate: str, year: int, mileage_at_start: int,
                            start_amount: int, **kwargs) -> Car:
        car = Car(name=car_plate, year=year, mileage_at_start=mileage_at_start, control_mileage=mileage_at_start,
                  model_id=model_id, car_investor_id=investor_id)
        car.investment = InvestmentCarBalance(name=car_plate, create_date=now().date())
        car.investment.save()
        car.save()
        Balance.form_transaction(Balance.DEPOSIT, [(car.investment, None, start_amount)])
        return car


class ExpensesProcessor:
    @staticmethod
    def form_expense(account: Account,
                     amount: int,
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
            transaction_record = Balance.form_transaction(Balance.EXPENSE, [(account, counterpart, amount)])
            expense = Expenses(
                account=account, counterpart=counterpart, expenseType=expense_type,
                description=description, transaction=transaction_record, amount=amount
            )
            expense.save()
            return expense

    @staticmethod
    def form_car_current_expense(car: Car,
                                 amount: int,
                                 expense_type: ExpensesTypes,
                                 counterpart: Counterpart,
                                 description: str) -> Expenses:
        if expense_type.type_class != ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE:
            raise TypeError('TypeError class only CAR_EXPENSE')
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
                                 expense_type: TypeError,
                                 counterpart: Counterpart,
                                 description: str) -> Expenses:
        if expense_type.type_class != ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE:
            raise TypeError('TypeError class only CAPITAL_CAR_EXPENSE')
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


class TripProcessor:
    @staticmethod
    def manual_create_taxi_trip(car: Car, driver: Driver, start: datetime, payer: Counterpart, millage: int,
                                amount: int, gas_price: int):
        taxitrip = TaxiTrip(car=car, timestamp=start, driver=driver, payer=payer, mileage=millage, amount=amount)
        fuel_trip = (millage + car.additional_miilage)/100 * car.fuel_consumption
        fuel_price = fuel_trip * gas_price
        taxitrip.fuel = math.ceil(fuel_price)
        pass
