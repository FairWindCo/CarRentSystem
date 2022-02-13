import math

from .utils import float_round


class InvestorCalc:
    def __init__(self, investment_income: float,
                 investor_profit: float = 50,
                 assistance_profit: float = 10,
                 use_ful_car_assistance=False
                 ) -> None:
        super().__init__()
        self.investor_profit_multiplier = investor_profit / 100
        if not use_ful_car_assistance:
            self.assistance_profit_multiplier = assistance_profit / 100
            self._assistance = investment_income * self.assistance_profit_multiplier
        else:
            self._assistance = 0
        self._car_profit = investment_income - self.assistance
        self._investor_profit = self._car_profit * self.investor_profit_multiplier
        self._firm_profit = self._car_profit - self.investor_profit

    @property
    # assistance в случае расчета от заработка (денег которые пришли от оператора)
    def assistance(self):
        return round(self._assistance, 2)

    @property
    # прибыль машины
    def car_profit(self):
        return round(self._car_profit, 2)

    @property
    # assistance в случае расчета от заработка (денег которые пришли от оператора) в формате для транзакции
    def assistance_many(self):
        return round(self._assistance * 100)

    @property
    # прибыль в формате для транзакции
    def car_profit_many(self):
        return round(self._car_profit * 100)

    @property
    # прибыль инвестора в формате для транзакции
    def investor_profit_many(self):
        return float_round(self._investor_profit * 100)

    @property
    # прибыль инвестора
    def investor_profit(self):
        return float_round(self._investor_profit, 2)

    @property
    # прибыль фирмы в формате для транзакции
    def firm_profit_many(self):
        return float_round(self._firm_profit * 100, 0, math.ceil)

    @property
    # прибыль фирмы
    def firm_profit(self):
        return float_round(self._firm_profit, 2, round)
