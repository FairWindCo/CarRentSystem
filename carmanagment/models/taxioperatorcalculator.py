import math


class TaxiCalculator:
    def __init__(self,
                 millage: float, amount: float, cash: float,
                 fuel_consumption: float, fuel_price: float, additional_millage: float = 0,
                 operator_cash_profit: float = 0.15,
                 cart_cash_profit: float = 0.15,
                 bank_profit: float = 0.025,
                 firm_profit: float = 50,
                 driver_profit: float = 50):
        self._cash = cash
        self._fuel_trip = (millage + additional_millage) / 100 * fuel_consumption
        self._fuel_price = self._fuel_trip * fuel_price
        # сумма денег Б\Н
        self._credit_cart_cash = amount - cash
        self._total_trip_many = amount
        # сумма комисии в пользу оператора такси
        self._payer_interest = cash * operator_cash_profit + self._credit_cart_cash * cart_cash_profit
        # сумма с поездки которая пришла на фирму
        self._trip_firm_total_many = amount - self._payer_interest
        # Расчет банковского процента с платежа
        clean_credit_cart_cash = self._credit_cart_cash - self._payer_interest
        if clean_credit_cart_cash > 0:
            self._bank_rent = clean_credit_cart_cash * bank_profit
        else:
            self._bank_rent = -self._payer_interest * bank_profit
        # Сумма денег без комисии таксопарка и банка
        self._trip_many_without_bank = self._trip_firm_total_many - self._bank_rent
        # Деньги пришедшие фирме без стоимости топлива
        self._real_amount = self._trip_many_without_bank - self._fuel_price
        # Операционные затраты фирмы на обслуживание парка
        self._operating_costs = self._trip_many_without_bank * (firm_profit / 100)
        # Зарплата водителя
        self._driver_money = self._real_amount * (driver_profit / 100)
        # Прибыль по машине (как часть прибыли инвестора и прибили фирмы)
        self._firm_profit = self._real_amount - self._driver_money - self._operating_costs
        # Общая сумма денег которые необходимо отдать оператору такси
        self._total_payer_amount = self._payer_interest + self._bank_rent
        # деньги который поступили - процент уклона - процент банка - наличные
        # по идее это должно упасть в кассу уклона
        if clean_credit_cart_cash > 0:
            self._credit_cart_many = clean_credit_cart_cash - self._bank_rent
        else:
            self._credit_cart_many = self._payer_interest + self._bank_rent

    @property
    def firm_profit(self):
        return round(self._firm_profit, 2)

    @property
    def total_payer_amount(self):
        return round(self._total_payer_amount, 2)

    @property
    def bank_rent(self):
        return round(self._bank_rent, 2)

    @property
    def driver_money(self):
        return round(self._driver_money, 2)

    @property
    def operating_costs(self):
        return round(self._operating_costs, 2)

    @property
    def real_amount(self):
        return round(self._real_amount, 2)

    @property
    def trip_firm_total_many(self):
        return round(self._trip_firm_total_many, 2)

    @property
    def credit_cart_cash(self):
        return round(self._credit_cart_cash, 2)

    @property
    def fuel_price(self):
        return round(self._fuel_price, 2)

    @property
    def fuel_trip(self):
        return self._fuel_trip

    @property
    def payer_interest(self):
        return round(self._payer_interest, 2)

    @property
    def total_trip_many(self):
        return round(self._total_trip_many, 2)

    @property
    def trip_many_without_bank(self):
        return round(self._trip_many_without_bank, 2)

    @property
    def cash(self):
        return round(self._cash, 2)

    @property
    def credit_cart_many(self):
        return round(self._credit_cart_many, 2)

    @property
    def firm_profit_int(self):
        return round(self._firm_profit * 100, 2)

    @property
    def total_payer_amount_int(self):
        return round(self._total_payer_amount * 100, 2)

    @property
    def bank_rent_int(self):
        return round(self._bank_rent * 100, 2)

    @property
    def driver_money_int(self):
        return round(self._driver_money * 100, 2)

    @property
    def operating_costs_int(self):
        return round(self._operating_costs * 100, 2)

    @property
    def real_amount_int(self):
        return round(self._real_amount * 100, 2)

    @property
    def trip_firm_total_many_int(self):
        return round(self._trip_firm_total_many * 100, 2)

    @property
    def credit_cart_cash_int(self):
        return round(self._credit_cart_cash * 100, 2)

    @property
    def fuel_price_int(self):
        return round(self._fuel_price * 100, 2)

    @property
    def payer_interest_int(self):
        return round(self._payer_interest * 100, 2)

    @property
    def total_trip_many_int(self):
        return round(self._total_trip_many * 100, 2)

    @property
    def trip_many_without_bank_int(self):
        return round(self._trip_many_without_bank * 100, 2)

    @property
    def cash_int(self):
        return round(self._cash * 100, 2)

    @property
    def credit_cart_many_int(self):
        return round(self._credit_cart_many * 100, 2)

    @property
    def firm_profit_f(self):
        return self._firm_profit

    @property
    def total_payer_amount_f(self):
        return self._total_payer_amount

    @property
    def bank_rent_f(self):
        return self._bank_rent

    @property
    def driver_money_f(self):
        return self._driver_money

    @property
    def operating_costs_f(self):
        return self._operating_costs

    @property
    def real_amount_f(self):
        return self._real_amount

    @property
    def trip_firm_total_many_f(self):
        return self._trip_firm_total_many

    @property
    def credit_cart_cash_f(self):
        return self._credit_cart_cash

    @property
    def fuel_price_f(self):
        return self._fuel_price

    @property
    def payer_interest_f(self):
        return self._payer_interest

    @property
    def total_trip_many_f(self):
        return self._total_trip_many

    @property
    def trip_many_without_bank_f(self):
        return self._trip_many_without_bank

    @property
    def cash_f(self):
        return self._cash

    @property
    def credit_cart_many_f(self):
        return self._credit_cart_many

    @property
    def firm_profit_tint(self):
        return math.trunc(self._firm_profit)

    @property
    def total_payer_amount_tint(self):
        return math.trunc(self._total_payer_amount)

    @property
    def bank_rent_tint(self):
        return math.trunc(self._bank_rent)

    @property
    def driver_money_tint(self):
        return math.trunc(self._driver_money)

    @property
    def operating_costs_tint(self):
        return math.trunc(self._operating_costs)

    @property
    def real_amount_tint(self):
        return math.trunc(self._real_amount)

    @property
    def trip_firm_total_many_tint(self):
        return math.trunc(self._trip_firm_total_many)

    @property
    def credit_cart_cash_tint(self):
        return math.trunc(self._credit_cart_cash)

    @property
    def fuel_price_tint(self):
        return math.trunc(self._fuel_price)
