import math


class TaxiCalculator:
    @classmethod
    def get_calculator(cls,
                       millage: float, amount: float, cash: float, gas_price: float, car, payer, driver):
        return cls(millage, amount, cash,
                   car.fuel_consumption,
                   gas_price,
                   car.additional_millage,
                   payer.cash_profit,
                   payer.profit,
                   payer.bank_interest,
                   car.car_investor.operating_costs_percent,
                   driver.profit,
                   car.car_investor.profit,
                   driver.fuel_compensation,
                   )

    def __init__(self,
                 millage: float, amount: float, cash: float,
                 fuel_consumption: float = 15,
                 fuel_price: float = 20,
                 additional_millage: float = 0,
                 operator_cash_profit: float = 17,
                 cart_cash_profit: float = 17,
                 bank_profit: float = 2.5,
                 firm_profit: float = 50,
                 driver_profit: float = 50,
                 investor_profit: float = 50,
                 fuel_compensation: float = 100,
                 use_bank_compensation=True,
                 use_ful_car_assistance=False):
        self._cash = cash
        # convert percent to multiplayer
        operator_cash_profit /= 100
        cart_cash_profit /= 100
        bank_profit /= 100
        fuel_compensation /= 100
        firm_profit /= 100
        driver_profit /= 100
        investor_profit /= 100
        # количество топлива
        self._fuel_trip = (millage + additional_millage) / 100 * fuel_consumption
        # цена топлива
        self._fuel_price = self._fuel_trip * fuel_price
        self._fuel_compensation = self._fuel_price * fuel_compensation
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
            self._bank_rent = -self._payer_interest * bank_profit if use_bank_compensation else 0
        # Сумма денег без комисии таксопарка и банка
        self._trip_many_without_bank = self._trip_firm_total_many - self._bank_rent
        # Деньги пришедшие фирме без стоимости топлива (компенсация топлива по проценту)
        self._real_amount = self._trip_many_without_bank - self._fuel_compensation
        # # Операционные затраты фирмы на обслуживание парка
        if use_ful_car_assistance:
            self._operating_costs = self._trip_many_without_bank * firm_profit
        # Зарплата водителя
        self._driver_money = self._real_amount * driver_profit
        if not use_ful_car_assistance:
        # Операционные затраты фирмы на обслуживание парка
            self._operating_costs = (self._real_amount - self._driver_money) * firm_profit

        # Прибыль по машине (как часть прибыли инвестора и прибили фирмы)
        self._car_amount = self._real_amount - self._driver_money

        self._clean_car_amount = self._car_amount - self._operating_costs
        # Прибыль инвестора
        self._investor_profit = self._clean_car_amount * investor_profit
        # прибыль фирмы
        self._firm_profit = self._clean_car_amount - self._investor_profit
        # Общая сумма денег которые необходимо отдать оператору такси
        self._total_payer_amount = self._payer_interest + self._bank_rent
        # деньги который поступили - процент уклона - процент банка - наличные
        # по идее это должно упасть в кассу уклона
        if clean_credit_cart_cash > 0:
            self._credit_cart_many = clean_credit_cart_cash - self._bank_rent
        else:
            self._credit_cart_many = self._payer_interest + self._bank_rent

        if self._firm_profit < 0 or self._investor_profit < 0 or self._driver_money < 0 or self._payer_interest < 0:
            raise ValueError('Отрицательные показатели в доходах фирмы, водителя и инвестора')

        m_sum = self.firm_profit + self.investor_profit + \
                self.driver_money + self.operating_costs + \
                self.fuel_compensation + \
                self.bank_rent + self.payer_interest
        if (m_sum - amount) > 1:
            raise ValueError(f'Не верный расчет {m_sum} != {amount}')

    @property
    # Прибыль по машине (как часть прибыли инвестора и прибили фирмы)
    def car_profit(self):
        return round(self._car_amount, 2)

    @property
    # Общая сумма денег которые необходимо отдать оператору такси
    def total_payer_amount(self):
        return round(self._total_payer_amount, 2)

    @property
    def bank_rent(self):
        return round(self._bank_rent, 2)

    @property
    # Зарплата водителя
    def driver_money(self):
        return round(self._driver_money, 2)

    @property
    # Операционные затраты фирмы на обслуживание парка
    def operating_costs(self):
        return round(self._operating_costs, 2)

    @property
    # Деньги пришедшие фирме без стоимости топлива (компенсация топлива по проценту)
    def real_amount(self):
        return round(self._real_amount, 2)

    @property
    # сумма с поездки которая пришла на фирму
    def trip_firm_total_many(self):
        return round(self._trip_firm_total_many, 2)

    @property
    # сумма денег Б\Н
    def credit_cart_cash(self):
        return round(self._credit_cart_cash, 2)

    @property
    # стоимость топлива
    def fuel_price(self):
        return round(self._fuel_price, 2)

    @property
    # потраченное топливо
    def fuel_trip(self):
        return self._fuel_trip

    @property
    # сумма комиссии в пользу оператора такси
    def payer_interest(self):
        return round(self._payer_interest, 2)

    @property
    # общая сумма за поездки
    def total_trip_many(self):
        return round(self._total_trip_many, 2)

    @property
    # Сумма денег без комисии таксопарка и банка
    def trip_many_without_bank(self):
        return round(self._trip_many_without_bank, 2)

    @property
    def cash(self):
        return round(self._cash, 2)

    @property
    def credit_cart_many(self):
        return round(self._credit_cart_many, 2)

    @property
    # Прибыль по машине (как часть прибыли инвестора и прибили фирмы)
    def car_profit_int(self):
        return round(self._car_amount * 100, 2)

    @property
    # Общая сумма денег которые необходимо отдать оператору такси
    def total_payer_amount_int(self):
        return round(self._total_payer_amount * 100, 2)

    @property
    # Комиссия банка (может быть отрицательной для наличных)
    def bank_rent_int(self):
        return round(self._bank_rent * 100, 2)

    @property
    # Зарплата водителя
    def driver_money_int(self):
        return round(self._driver_money * 100, 2)

    @property
    # Операционные затраты фирмы на обслуживание парка
    def operating_costs_int(self):
        return round(self._operating_costs * 100, 2)

    @property
    # Деньги пришедшие фирме без стоимости топлива (компенсация топлива по проценту)
    def real_amount_int(self):
        return round(self._real_amount * 100, 2)

    @property
    # сумма с поездки которая пришла на фирму
    def trip_firm_total_many_int(self):
        return round(self._trip_firm_total_many * 100, 2)

    @property
    # сумма денег Б\Н
    def credit_cart_cash_int(self):
        return round(self._credit_cart_cash * 100, 2)

    @property
    # стоимость топлива
    def fuel_price_int(self):
        return round(self._fuel_price * 100, 2)

    @property
    # сумма комиссии в пользу оператора такси
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
    # Прибыль по машине (как часть прибыли инвестора и прибили фирмы)
    def car_profit_f(self):
        return self._car_amount

    @property
    # Общая сумма денег которые необходимо отдать оператору такси
    def total_payer_amount_f(self):
        return self._total_payer_amount

    @property
    # комиссия банка
    def bank_rent_f(self):
        return self._bank_rent

    @property
    # Зарплата водителя
    def driver_money_f(self):
        return self._driver_money

    @property
    # Операционные затраты фирмы на обслуживание парка
    def operating_costs_f(self):
        return self._operating_costs

    @property
    # Деньги пришедшие фирме без стоимости топлива (компенсация топлива по проценту)
    def real_amount_f(self):
        return self._real_amount

    @property
    # сумма с поездки которая пришла на фирму
    def trip_firm_total_many_f(self):
        return self._trip_firm_total_many

    @property
    # сумма денег Б\Н
    def credit_cart_cash_f(self):
        return self._credit_cart_cash

    @property
    # стоимость топлива
    def fuel_price_f(self):
        return self._fuel_price

    @property
    # сумма комиссии в пользу оператора такси
    def payer_interest_f(self):
        return self._payer_interest

    @property
    # общая сумма за поездки
    def total_trip_many_f(self):
        return self._total_trip_many

    @property
    # Сумма денег без комисии таксопарка и банка
    def trip_many_without_bank_f(self):
        return self._trip_many_without_bank

    @property
    # сумма наличных
    def cash_f(self):
        return self._cash

    @property
    # сумма денег Б\Н
    def credit_cart_many_f(self):
        return self._credit_cart_many

    @property
    # Прибыль по машине (как часть прибыли инвестора и прибили фирмы)
    def car_profit_tint(self):
        return math.trunc(self._car_amount)

    @property
    # Общая сумма денег которые необходимо отдать оператору такси
    def total_payer_amount_tint(self):
        return math.trunc(self._total_payer_amount)

    @property
    def bank_rent_tint(self):
        return math.trunc(self._bank_rent)

    @property
    # Зарплата водителя
    def driver_money_tint(self):
        return math.trunc(self._driver_money)

    @property
    # Операционные затраты фирмы на обслуживание парка
    def operating_costs_tint(self):
        return math.trunc(self._operating_costs)

    @property
    # Деньги пришедшие фирме без стоимости топлива (компенсация топлива по проценту)
    def real_amount_tint(self):
        return math.trunc(self._real_amount)

    @property
    # сумма с поездки которая пришла на фирму
    def trip_firm_total_many_tint(self):
        return math.trunc(self._trip_firm_total_many)

    @property
    # сумма денег Б\Н
    def credit_cart_cash_tint(self):
        return math.trunc(self._credit_cart_cash)

    @property
    # стоимость топлива
    def fuel_price_tint(self):
        return math.trunc(self._fuel_price)

    @property
    # Прибыль инвестора
    def investor_profit_f(self):
        return self._investor_profit

    @property
    # прибыль фирмы
    def firm_profit_int(self):
        return int(self._firm_profit)

    @property
    # Прибыль инвестора
    def investor_profit_int(self):
        return int(self._investor_profit)

    @property
    # прибыль фирмы
    def firm_profit_f(self):
        return self._firm_profit

    @property
    # Прибыль инвестора
    def investor_profit_tint(self):
        return math.trunc(self._investor_profit)

    @property
    # прибыль фирмы
    def firm_profit_tint(self):
        return math.trunc(self._firm_profit)

    @property
    # Прибыль инвестора
    def investor_profit(self):
        return round(self._investor_profit, 2)

    @property
    # прибыль фирмы
    def firm_profit(self):
        return round(self._firm_profit, 2)

    @property
    # стоимость топлива
    def fuel_compensation(self):
        return round(self._fuel_compensation, 2)

    @property
    # стоимость топлива
    def fuel_compensation_f(self):
        return self._fuel_compensation

    @property
    # стоимость топлива
    def fuel_compensation_int(self):
        return round(self._fuel_compensation * 100, 2)

    @property
    # стоимость топлива
    def fuel_compensation_tint(self):
        return math.trunc(self._fuel_compensation)
