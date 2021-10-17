import datetime
import math

from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.timezone import now

from balance.models import Account
from balance.services import Balance
from carmanagment.models import Expenses, ExpensesTypes, Counterpart, Car, CarModel, InvestmentCarBalance, Investor, \
    TaxiTrip, TripStatistics


class CarCreator:
    @staticmethod
    def add_new_car(investor: Investor, model: CarModel, car_plate: str, year: int, mileage_at_start: int,
                    start_amount: int) -> Car:
        return CarCreator.add_new_car_from_id(name=car_plate, year=year, mileage_at_start=mileage_at_start,
                                              start_amount=start_amount,
                                              model_id=model.pk, investor_id=investor.pk)

    @staticmethod
    def add_new_car_from_id(investor_id: int, model_id: int, car_plate: str, year: int, mileage_at_start: int,
                            start_amount: int, **kwargs) -> Car:
        car = Car(name=car_plate, year=year, mileage_at_start=mileage_at_start, control_mileage=mileage_at_start,
                  model_id=model_id, car_investor_id=investor_id)
        car.investment = InvestmentCarBalance(name=car_plate, create_date=now().date())
        car.investment.save()
        car.save()
        Balance.form_transaction(Balance.DEPOSIT, [
            (car.investment, None, start_amount * 100, 'Инвестиция')
        ], f'Включение авто {car_plate} {start_amount}$')
        return car


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


def get_sum(dict_obj, name):
    value = dict_obj.get(name, None)
    return value if value is not None else 0


class Statistics:
    @staticmethod
    def create_car_statistics(car: Car, statistics_date: datetime.date):
        from django.db.models import Sum, Count
        if statistics_date is None:
            statistics_date = datetime.datetime.now()
        statistics_start_date: datetime.date = statistics_date.date()
        statistics_end_date: datetime.date = statistics_start_date + datetime.timedelta(days=1)
        expenses_sum = Expenses.objects.filter(account=car,
                                               date_mark__lte=statistics_end_date,
                                               date_mark__gte=statistics_start_date).aggregate(Sum('amount'))
        trip_sum = TaxiTrip.objects.filter(car=car,
                                           timestamp__lte=statistics_end_date,
                                           timestamp__gte=statistics_start_date). \
            aggregate(Sum('mileage'),
                      Sum('fuel'),
                      Sum('amount'),
                      Sum('car_amount'),
                      Sum('payer_amount'),
                      Sum('driver_amount'),
                      Count('pk')
                      )
        try:
            TripStatistics(car=car,
                           stat_date=statistics_start_date,
                           mileage=get_sum(trip_sum, 'mileage__sum'),
                           fuel=get_sum(trip_sum, 'fuel__sum'),
                           amount=get_sum(trip_sum, 'amount__sum'),
                           car_amount=get_sum(trip_sum, 'car_amount__sum'),
                           driver_amount=get_sum(trip_sum, 'driver_amount__sum'),
                           payer_amount=get_sum(trip_sum, 'payer_amount__sum'),
                           expanse_amount=get_sum(expenses_sum, 'amount__sum'),
                           trip_count=get_sum(trip_sum, 'pk__count'),
                           ).save()
        except IntegrityError as e:
            stat = TripStatistics.objects.get(car=car, stat_date=statistics_start_date)
            stat.mileage = get_sum(trip_sum, 'mileage__sum')
            stat.fuel = get_sum(trip_sum, 'fuel__sum')
            stat.amount = get_sum(trip_sum, 'amount__sum')
            stat.car_amount = get_sum(trip_sum, 'car_amount__sum')
            stat.driver_amount = get_sum(trip_sum, 'driver_amount__sum')
            stat.payer_amount = get_sum(trip_sum, 'payer_amount__sum')
            stat.expanse_amount = get_sum(expenses_sum, 'amount__sum')
            stat.trip_count = get_sum(trip_sum, 'pk__count')
            stat.save()

    @staticmethod
    def create_statistics(statistics_date: datetime.date = None):
        if statistics_date is None:
            statistics_date = datetime.datetime.now()

        cars = Car.objects.all()

        for car in cars:
            Statistics.create_car_statistics(car, statistics_date)

    @staticmethod
    def get_last_statistics():
        cars = Car.objects.all()
        return {car.name: list(car.tripstatistics_set.order_by('-stat_date').all()[:7]) for car in cars}
