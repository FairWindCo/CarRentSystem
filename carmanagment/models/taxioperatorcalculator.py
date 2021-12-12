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
        self._fuel_price = round(self._fuel_trip * fuel_price, 2)
        # сумма денег Б\Н
        self._credit_cart_cash = amount - cash
        self._total_trip_many = amount
        # сумма комисии в пользу оператора такси
        self._payer_interest = round(cash * operator_cash_profit + self._credit_cart_cash * cart_cash_profit, 2)
        # сумма с поездки которая пришла на фирму
        self._trip_firm_total_many = round(amount - self._payer_interest, 2)
        # Расчет банковского процента с платежа
        clean_credit_cart_cash = self._credit_cart_cash - self._payer_interest
        if clean_credit_cart_cash > 0:
            self._bank_rent = round(clean_credit_cart_cash * bank_profit, 2)
        else:
            self._bank_rent = round(- self._payer_interest * bank_profit, 2)
        # Сумма денег без комисии таксопарка и банка
        self._trip_many_without_bank = self._trip_firm_total_many - self._bank_rent
        # Деньги пришедшие фирме без стоимости топлива
        self._real_amount = round(self._trip_many_without_bank - self._fuel_price, 2)
        # Операционные затраты фирмы на обслуживание парка
        self._operating_costs = round(self._trip_many_without_bank * (firm_profit / 100), 2)
        # Зарплата водителя
        self._driver_money = round(self._real_amount * (driver_profit / 100), 2)
        # Прибыль по машине (как часть прибыли инвестора и прибили фирмы)
        self._firm_profit = round(self._real_amount - self._driver_money - self._operating_costs, 2)
        # Общая сумма денег которые необходимо отдать оператору такси
        self._total_payer_amount = self._payer_interest + self._bank_rent

        self._credit_cart_many = self._trip_many_without_bank - self.cash

    @property
    def firm_profit(self):
        return self._firm_profit

    @property
    def total_payer_amount(self):
        return self._total_payer_amount

    @property
    def bank_rent(self):
        return self._bank_rent

    @property
    def driver_money(self):
        return self._driver_money

    @property
    def operating_costs(self):
        return self._operating_costs

    @property
    def real_amount(self):
        return self._real_amount

    @property
    def trip_firm_total_many(self):
        return self._trip_firm_total_many

    @property
    def credit_cart_cash(self):
        return self._credit_cart_cash

    @property
    def fuel_price(self):
        return self._fuel_price

    @property
    def fuel_trip(self):
        return self._fuel_trip

    @property
    def payer_interest(self):
        return self._payer_interest

    @property
    def total_trip_many(self):
        return self._total_trip_many

    @property
    def trip_many_without_bank(self):
        return self._trip_many_without_bank

    @property
    def cash(self):
        return self._cash

    @property
    def credit_cart_many(self):
        return self._credit_cart_many
