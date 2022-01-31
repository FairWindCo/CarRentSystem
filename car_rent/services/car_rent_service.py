from django.db import transaction

from balance.models import Account
from balance.services import Balance
from car_management.models import Car


class CarRentService:

    @classmethod
    def move_rent_many(cls, car: Car, amount: float, firm: Account):
        if car and amount > 0:
            sum_many = round(amount * 100)
            investor = car.car_investor
            if investor:
                profit = investor.profit
                if profit < 0:
                    profit = 0
                if profit > 100:
                    profit = 100
                firm_profit = 100 - profit
                rent_money = sum_many / profit * 100
                balance = car.get_current_balance()
                print(f'Balance {balance} for car {car.name}')
                if balance < rent_money:
                    return False, 'Не достаточно средств'
                firm_many = round(rent_money * firm_profit / 100)
                with transaction.atomic():
                    transaction_record = Balance.form_transaction(Balance.WITHDRAWAL, [
                        (car, investor, sum_many, 'Прибыль инвестора'),
                        (car, firm, firm_many, 'Прибыль фирмы'),
                    ], 'Вывод прибыли')
                return True, transaction_record
        return False, 'Не верные данные для проведения'
