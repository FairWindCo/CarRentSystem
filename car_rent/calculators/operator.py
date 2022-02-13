import cmath
import math

from .utils import float_round


class OperatorCalc:
    def __init__(self, amount: float, cash: float,
                 operator_cash_profit: float = 17,
                 cart_cash_profit: float = 17,
                 bank_profit: float = 2.5,
                 tax: float = 0,
                 use_bank_compensation=True
                 ) -> None:
        super().__init__()
        self.operator_cash_profit_multiplier = operator_cash_profit / 100
        self.cart_cash_profit_multiplier = cart_cash_profit / 100
        self.bank_profit_multiplier = bank_profit / 100
        self.tax_multiplier = tax / 100
        self._credit_cart_cash = amount - cash
        # сумма комиcсия в пользу оператора такси
        self._payer_interest = cash * self.operator_cash_profit_multiplier + \
                               self._credit_cart_cash * self.cart_cash_profit_multiplier
        # сумма налога с (как бы прибыли от поездки)
        self._tax = (self._credit_cart_cash - self._payer_interest) * self.tax_multiplier

        # Расчет банковского процента с платежа (считаем сколько есть денег на счете)
        clean_credit_cart_cash = self._credit_cart_cash - self._payer_interest - self._tax
        if clean_credit_cart_cash > 0:
            # если суммы достаточно высчитываем процент, который уйдет банку
            self._bank_rent = clean_credit_cart_cash * self.bank_profit_multiplier
        else:
            # если денег на счете нет, то считаем процент как бы для компенсации, того, что эти деньги не взяли
            self._bank_rent = -self._payer_interest * self.bank_profit_multiplier if use_bank_compensation else 0
        # ВАЖНО! отнять от всей суммы уже округленные значения, так как сумма будет фигурировать в расчетах далее
        self._trip_rent = amount - self.aggregator_losses
        self._taxi_aggregator_corrections = self.aggregator_losses - self._credit_cart_cash

    @property
    # Комиссия агрегатора
    def taxi_aggregator_corrections(self):
        return round(self._taxi_aggregator_corrections, 2)

    @property
    # Комиссия агрегатора в виде для транзакций
    def taxi_aggregator_corrections_many(self):
        return round(self._taxi_aggregator_corrections * 100)

    @property
    # Комиссия агрегатора
    def taxi_aggregator_rent(self):
        return round(self._payer_interest, 2)

    @property
    # Комиссия банка
    def bank_rent(self):
        return round(self._bank_rent, 2)

    @property
    # Комиссия агрегатора в виде для транзакций
    def taxi_aggregator_rent_many(self):
        return round(self._payer_interest * 100)

    @property
    # Комиссия банка в виде для транзакций
    def bank_rent_many(self):
        return round(self._bank_rent * 100)

    @property
    # Налог в виде для транзакций
    def trip_tax_many(self):
        return round(self._tax * 100)

    @property
    # Заработок в виде для транзакций
    def earnings_many(self):
        return round(self._trip_rent * 100)

    @property
    # Налог в виде для транзакций
    def trip_tax(self):
        return round(self._tax, 2)

    @property
    # Заработок
    def earnings(self):
        return round(self._trip_rent, 2)

    @property
    # Общая сумма денег которые необходимо отдать оператору такси
    def aggregator_losses(self):
        return float_round(self._payer_interest + self._bank_rent + self._tax, 2, math.ceil)

    @property
    # Заработок
    def earnings_clean(self):
        return self._trip_rent
