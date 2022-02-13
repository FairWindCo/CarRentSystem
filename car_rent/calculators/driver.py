from car_rent.calculators.utils import float_round


class DriverCalc:
    def __init__(self, earnings: float,
                 fuel_cost: float,
                 driver_profit: float = 50,
                 assistance_profit: float = 10,
                 use_ful_car_assistance=False
                 ) -> None:
        super().__init__()
        self.driver_profit_multiplier = driver_profit / 100
        if use_ful_car_assistance:
            self.assistance_profit_multiplier = assistance_profit / 100
            self._assistance = earnings * self.assistance_profit_multiplier
        else:
            self._assistance = 0
        self._income = earnings - fuel_cost - self.assistance
        self._driver_salary = self._income * self.driver_profit_multiplier
        self._investment_income = self._income - self.driver_salary

    @property
    # assistance в случае расчета от заработка (денег которые пришли от оператора)
    def assistance(self):
        return round(self._assistance, 2)

    @property
    # доход машины
    def car_income(self):
        return round(self._income, 2)

    @property
    # assistance в случае расчета от заработка (денег которые пришли от оператора) в формате для транзакции
    def assistance_many(self):
        return round(self._assistance * 100)

    @property
    # доход машины в формате для транзакции
    def car_income_many(self):
        return round(self._income * 100)

    @property
    # ЗП водителя в формате для транзакции
    def driver_salary_many(self):
        return float_round(self._driver_salary * 100)

    @property
    # ЗП водителя
    def driver_salary(self):
        return float_round(self._driver_salary, 2)

    @property
    # инвестиционный доход в формате для транзакции
    def investment_income_many(self):
        return round(self._investment_income * 100)

    @property
    # инвестиционный доход
    def investment_income(self):
        return round(self._investment_income, 2)

    @property
    # инвестиционный доход
    def investment_clean(self):
        return self._investment_income
