from constance import config

from balance.services import Balance
from car_management.models import Car, Driver
from car_management.models.rent_price import PaidType
from car_rent.calculators import TripCalculator
from car_rent.models import TaxiOperator
from constance import config

from balance.services import Balance
from car_management.models import Car, Driver
from car_rent.calculators import TripCalculator
from car_rent.models import TaxiOperator


def make_operations_for_transaction_full(car: Car, driver: Driver, payer: TaxiOperator, calc: TripCalculator,
                                         many_cash_box, start):
    firm_account = config.FIRM
    if firm_account is None:
        raise ValueError('Need Set Firm account in Config')
    operations = [
        (None, payer, calc.amount_many, 'Платеж от клиента'),
        (payer, None, calc.taxi_aggregator_rent_many, 'Комисия оператора такси'),
        (payer, car, calc.earnings_many, 'Платеж от оператора'),
        (car, driver, calc.fuel_compensation_money, 'Компенсация топлива'),
        (car, firm_account, calc.assistance_many, 'Операционные затраты'),
        (car, driver, calc.driver_salary, 'Зарплата водителя'),
    ]
    if calc.cash > 0:
        operations.append((driver, None, calc.cash_many, 'Вывод наличных'))
    if calc.bank_rent > 0:
        operations.append((payer, None, calc.bank_rent_many, 'Комисия банка'))
    else:
        operations.append(
            (None, payer, abs(calc.bank_rent_many), 'возврат комисии банка за комисию оператора'))
    if many_cash_box:
        operations.append((None, driver, calc.cash_many, 'Внос денег в кассу'))
        operations.append((None, many_cash_box, calc.cash_many, 'Пополнение кассы'))
    if payer.cash_box:
        payer_balance_cache = calc.taxi_aggregator_corrections_many
        if payer_balance_cache < 0:
            operations.append(
                (None, payer.cash_box, payer_balance_cache,
                 f'Пополнение кассы {payer.cash_box.name} за '
                 f'поездку {start} {car.name} {driver.name}'))
        else:
            operations.append(
                (payer.cash_box, None, payer_balance_cache,
                 f'Снятие с кассы {payer.cash_box.name} за '
                 f'поездку {start} {car.name} {driver.name}'))
    return operations


def make_operations_for_transaction_simple(car: Car, driver: Driver, payer: TaxiOperator,
                                           calc: TripCalculator,
                                           many_cash_box, start):
    firm_account = config.FIRM
    if firm_account is None:
        raise ValueError('Need Set Firm account in Config')

    operations = [
        (None, car, calc.car_profit_many, 'Доход машины'),
        (None, firm_account, calc.assistance_many, 'Операционные затраты'),
    ]
    driver_corrections = calc.driver_correction
    if driver_corrections > 0:
        if many_cash_box:
            operations.append((driver, many_cash_box, calc.cash_many, 'Пополнение кассы'))
        else:
            operations.append((driver, None, driver_corrections, 'Начисление на баланс'))
    else:
        if many_cash_box:
            operations.append((many_cash_box, driver, driver_corrections, 'Вывод наличных'))
        else:
            operations.append((None, driver, driver_corrections, 'Вывод наличных'))

    if calc.cash > 0:
        operations.append((driver, None, calc.cash_many, 'Вывод наличных'))
    if calc.bank_rent > 0:
        operations.append((payer, None, calc.bank_rent_many, 'Комисия банка'))
    else:
        operations.append(
            (None, payer, abs(calc.bank_rent_many), 'возврат комисии банка за комисию оператора'))
    if many_cash_box:
        operations.append((None, driver, calc.cash_many, 'Внос денег в кассу'))
        operations.append((None, many_cash_box, calc.cash_many, 'Пополнение кассы'))

    if payer.cash_box:
        payer_balance_cache = calc.taxi_aggregator_corrections_many
        if payer_balance_cache < 0:
            operations.append(
                (None, payer.cash_box, payer_balance_cache,
                 f'Пополнение кассы {payer.cash_box.name} за '
                 f'поездку {start} {car.name} {driver.name}'))
        else:
            operations.append(
                (payer.cash_box, None, payer_balance_cache,
                 f'Снятие с кассы {payer.cash_box.name} за '
                 f'поездку {start} {car.name} {driver.name}'))
    return operations


def make_transactions_for_trip(car: Car, driver: Driver, payer: TaxiOperator, calc: TripCalculator, many_cash_box,
                               start, comment, transaction_saving: PaidType):
    if transaction_saving == PaidType.NO_TRANSACTION:
        return None
    elif transaction_saving == PaidType.FULL_TRANSACTION:
        operations = make_operations_for_transaction_full(car, driver, payer, calc, many_cash_box, start)
    else:
        operations = make_operations_for_transaction_simple(car, driver, payer, calc, many_cash_box, start)
    transaction_record = Balance.form_transaction(Balance.DEPOSIT, operations, comment if comment
    else f'Поездка {start} {car.name} {driver.name}')
    return transaction_record
