from .driver import DriverCalc
from .fuel import FuelCalculator
from .investor import InvestorCalc
from .operator import OperatorCalc


class TripCalculator:
    @classmethod
    def get_calculator(cls,
                       millage: float, amount: float, cash: float, gas_price: float, car, payer, terms):
        return cls(millage, amount, cash,
                   car.fuel_consumption,
                   gas_price,
                   terms.additional_millage,
                   payer.cash_profit,
                   payer.profit,
                   payer.bank_interest,
                   payer.tax,
                   car.car_investor.operating_costs_percent,
                   terms.profit,
                   car.car_investor.profit,
                   terms.fuel_compensation,
                   )

    def __init__(self,
                 millage: float, amount: float, cash: float,
                 fuel_consumption: float = 15,
                 fuel_price: float = 20,
                 additional_millage: float = 0,
                 operator_cash_profit: float = 17,
                 cart_cash_profit: float = 17,
                 bank_profit: float = 2.5,
                 tax: float = 0,
                 assistance_profit: float = 50,
                 driver_profit: float = 50,
                 investor_profit: float = 50,
                 fuel_compensation: float = 100,
                 use_bank_compensation=True,
                 use_ful_car_assistance=False):
        self._amount = amount
        self._cash = cash
        self._credit = amount - cash

        self.fuel_calc = FuelCalculator(millage, additional_millage, fuel_consumption, fuel_price, fuel_compensation)
        self.operator_calc = OperatorCalc(amount, cash, operator_cash_profit, cart_cash_profit, bank_profit, tax,
                                          use_bank_compensation)
        self.driver_calc = DriverCalc(self.operator_calc.earnings_clean, self.fuel_calc.fuel_cost, driver_profit,
                                      assistance_profit,
                                      use_ful_car_assistance)
        self.investor_calc = InvestorCalc(self.driver_calc.investment_clean, investor_profit, assistance_profit,
                                          use_ful_car_assistance)

        self._driver_many = self.fuel_calc.fuel_compensation + self.driver_calc.driver_salary
        self._driver_balance_correction = self._driver_many - cash
        _sum = round(self.aggregator_losses + self._driver_many + self.assistance + \
               self.investor_calc.firm_profit + self.investor_calc.investor_profit, 2)
        if self._amount != _sum:
            raise ValueError(f'Сумма всех платежей не сходится {self._amount}<>{_sum}')

    @property
    def cash(self):
        return self._cash

    @property
    def cash_many(self):
        return round(self._cash * 100, 2)

    @property
    def amount(self):
        return self._amount

    @property
    def amount_many(self):
        return round(self._amount * 100, 2)

    @property
    def credit_cash(self):
        return self._credit

    @property
    def credit_cash_many(self):
        return round(self._credit * 100, 2)

    @property
    # пробег с дополнительным учетом
    def millage(self):
        return self.fuel_calc.millage

    @property
    # затраченное топливо
    def fuel_trip(self):
        return self.fuel_calc.fuel_trip

    @property
    # стоимость топлива
    def fuel_cost(self):
        return self.fuel_calc.fuel_cost

    @property
    # компенсация за топливо водителю
    def fuel_compensation(self):
        return self.fuel_calc.fuel_compensation

    @property
    # компенсация за топливо водителю в формате транзакции
    def fuel_compensation_money(self):
        return self.fuel_calc.fuel_compensation_money

    @property
    # затраты на топливо
    def fuel_rest(self):
        return self.fuel_calc.fuel_rest

    @property
    # затраты на топливо в формате транзакции
    def fuel_rest_money(self):
        return self.fuel_calc.fuel_rest_money

    @property
    # Комиссия агрегатора
    def taxi_aggregator_rent(self):
        return self.operator_calc.taxi_aggregator_rent

    @property
    # Комиссия банка
    def bank_rent(self):
        return self.operator_calc.bank_rent

    @property
    # Комиссия агрегатора в виде для транзакций
    def taxi_aggregator_rent_many(self):
        return self.operator_calc.taxi_aggregator_rent_many

    @property
    # Комиссия банка в виде для транзакций
    def bank_rent_many(self):
        return self.operator_calc.bank_rent_many

    @property
    # Налог в виде для транзакций
    def trip_tax_many(self):
        return self.operator_calc.trip_tax_many

    @property
    # Заработок в виде для транзакций
    def earnings_many(self):
        return self.operator_calc.earnings_many

    @property
    # Налог в виде для транзакций
    def trip_tax(self):
        return self.operator_calc.trip_tax

    @property
    # Заработок
    def earnings(self):
        return self.operator_calc.earnings

    @property
    # Общая сумма денег которые необходимо отдать оператору такси
    def aggregator_losses(self):
        return self.operator_calc.aggregator_losses

    @property
    # assistance в случае расчета от заработка (денег которые пришли от оператора)
    def assistance(self):
        return self.driver_calc.assistance + self.investor_calc.assistance

    @property
    # доход машины
    def car_income(self):
        return self.driver_calc.car_income

    @property
    # assistance в случае расчета от заработка (денег которые пришли от оператора) в формате для транзакции
    def assistance_many(self):
        return self.driver_calc.assistance_many + self.investor_calc.assistance_many

    @property
    # доход машины в формате для транзакции
    def car_income_many(self):
        return self.driver_calc.car_income_many

    @property
    # ЗП водителя в формате для транзакции
    def driver_salary_many(self):
        return self.driver_calc.driver_salary_many

    @property
    # ЗП водителя
    def driver_salary(self):
        return self.driver_calc.driver_salary

    @property
    # инвестиционный доход в формате для транзакции
    def investment_income_many(self):
        return self.driver_calc.investment_income_many

    @property
    # инвестиционный доход
    def investment_income(self):
        return self.driver_calc.investment_income

    @property
    # прибыль машины
    def car_profit(self):
        return self.investor_calc.car_profit

    @property
    # прибыль в формате для транзакции
    def car_profit_many(self):
        return self.investor_calc.car_profit_many

    @property
    # прибыль инвестора в формате для транзакции
    def investor_profit_many(self):
        return self.investor_calc.investor_profit_many

    @property
    # прибыль инвестора
    def investor_profit(self):
        return self.investor_calc.investor_profit

    @property
    # прибыль фирмы в формате для транзакции
    def firm_profit_many(self):
        return self.investor_calc.firm_profit_many

    @property
    # прибыль фирмы
    def firm_profit(self):
        return self.investor_calc.firm_profit

    @property
    # полная сумма денег водителя
    def driver(self):
        return self._driver_many

    @property
    # полная сумма денег водителя в формате для транзакции
    def driver_many(self):
        return self._driver_many * 100

    @property
    # коррекция баланса водителя
    def driver_correction(self):
        return self._driver_balance_correction

    @property
    # коррекция баланса водителя в формате для транзакции
    def driver_correction_many(self):
        return self._driver_balance_correction * 100

    @property
    # Комиссия агрегатора
    def taxi_aggregator_corrections(self):
        return self.operator_calc.taxi_aggregator_corrections

    @property
    # Комиссия агрегатора в виде для транзакций
    def taxi_aggregator_corrections_many(self):
        return self.operator_calc.taxi_aggregator_corrections_many
