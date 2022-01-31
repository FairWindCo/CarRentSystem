from django.test import TestCase
# Create your tests here.
from django.utils.timezone import now

# Create your tests here.
from balance.services import Balance
from car_management.models import CarBrand, CarModel, Investor, Driver
from car_management.serivices.car_service import CarCreator
from car_rent.models import TaxiOperator
from trips.models.taxi import TaxiTrip


class CheckTaxiTrip(TestCase):
    def setUp(self):
        self.brand = CarBrand(name='KIA')
        self.brand.save()
        self.model = CarModel(name='CEED', brand=self.brand)
        self.model.save()
        self.investor = Investor(name='test investor', profit=20)
        self.investor.save()
        self.driver = Driver(name='Taxi Driver', profit=50)
        self.driver.save()
        self.counterpart = TaxiOperator(name='Taxi service', profit=0, cash_profit=0)
        self.counterpart.save()
        self.car = CarCreator.add_new_car(self.investor, self.model, 'AA1919OO', 2013, 100000, 10000)
        self.car.fuel_consumption = 10
        self.car.save()

    def test_correct_taxi_trip(self):
        current_date = now()
        self.assertEquals(Balance.get_current_balance(self.driver), 0)
        self.assertEquals(Balance.get_current_balance(self.counterpart), 0)
        TaxiTrip.manual_create_taxi_trip(self.car, self.driver, current_date, self.counterpart, 100, 280, 12, False)
        fuel_price = 100*self.car.fuel_consumption/100*12
        driver_profit = (280 - fuel_price) * self.driver.profit / 100
        self.assertEquals(Balance.get_current_balance(self.counterpart), -28000)
        self.assertEquals(Balance.get_current_balance(self.driver), (fuel_price + driver_profit)*100)
        self.assertEquals(Balance.get_current_balance(self.car), 28000 - (fuel_price + driver_profit)*100)

    def test_correct_cash_taxi_trip(self):
        current_date = now()
        self.assertEquals(Balance.get_current_balance(self.driver), 0)
        self.assertEquals(Balance.get_current_balance(self.counterpart), 0)
        TaxiTrip.manual_create_taxi_trip(self.car, self.driver, current_date, self.counterpart, 100, 280, 12, True)
        fuel_price = 100*self.car.fuel_consumption/100*12
        driver_profit = (280 - fuel_price) * self.driver.profit / 100
        self.assertEquals(Balance.get_current_balance(self.counterpart), -28000)
        self.assertEquals(Balance.get_current_balance(self.driver), -28000 + fuel_price*100 + driver_profit*100)
        self.assertEquals(Balance.get_current_balance(self.car), 28000 - (fuel_price + driver_profit)*100)
