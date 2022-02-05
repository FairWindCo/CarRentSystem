import math


class FuelCalculator:

    def __init__(self, millage: float,
                 additional_millage: float = 0,
                 fuel_consumption: float = 15,
                 fuel_price: float = 20,
                 fuel_compensation: float = 100,

                 ) -> None:
        super().__init__() #38.41
        self._fuel_compensation_multiplier = fuel_compensation / 100
        self._full_millage = millage + additional_millage
        self._fuel_trip = self._full_millage / 100 * fuel_consumption
        self._fuel_price = self._fuel_trip * fuel_price
        self._fuel_compensation = self._fuel_price * self._fuel_compensation_multiplier

    @property
    def millage(self):
        return round(self._full_millage, 2)

    @property
    def fuel_trip(self):
        return round(self._fuel_trip, 2)

    @property
    def fuel_cost(self):
        return round(self._fuel_price, 2)

    @property
    def fuel_compensation(self):
        return round(self._fuel_compensation, 2)

    @property
    def fuel_compensation_money(self):
        return math.ceil(self._fuel_compensation * 100)

    @property
    def fuel_rest(self):
        return round(self._fuel_price - self.fuel_compensation, 2)

    @property
    def fuel_rest_money(self):
        return math.ceil(self._fuel_price - self.fuel_compensation * 100)
