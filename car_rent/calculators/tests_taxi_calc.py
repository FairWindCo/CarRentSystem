from django.test import TestCase

from car_rent.calculators import TripCalculator


def special_property(func):
    def getter(self):
        return func(self)
    print(func.name)


class CheckTaxiCaclculator(TestCase):
    def test_only_credit_cart_cash_trip(self):
        calc = TripCalculator(4.49, 82, 0,
                              14, 19.0476470588235, 4,
                              15, 15, 2.5, 0,
                              5, 50)

        self.assertEquals(calc.cash, 0, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cash, 82, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.taxi_aggregator_rent, 12.3, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, 1.74, 'Не совпадает комисия банка')
        self.assertEquals(calc.assistance, 1.13, 'Не совпадает комисия фирмы')
        self.assertEquals(calc.driver_salary, 22.66, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.investment_income, 22.66, 'Не совпадает прибыль машины')
        self.assertEquals(calc.fuel_compensation, 22.64, 'fuel')
        self.assertEquals(calc.earnings, 67.96, 'Деньги пришли на фирму')


    def test_only_cash_trip(self):
        calc = TripCalculator(3.18, 80, 80,
                              14, 19.0476470588235, 4,
                              15, 15, 2.5, 0,
                              5, 50)

        self.assertEquals(calc.cash, 80, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cash, 0, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.taxi_aggregator_rent, 12, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, -0.3, 'Не совпадает комисия банка')
        self.assertEquals(calc.assistance, 1.23, 'Не совпадает комисия фирмы')
        self.assertEquals(calc.driver_salary, 24.57, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.investment_income, 24.58, 'Не совпадает прибыль машины')
        self.assertEquals(calc.car_income, 49.15, 'Деньги пришли на фирму без топлива')

    def test_mix_cash_trip(self):
        calc = TripCalculator(7.01, 149, 94,
                              14, 19.0476470588235, 4,
                              15, 15, 2.5, 0,
                              5, 50)

        self.assertEquals(calc.cash, 94, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cash, 55, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.taxi_aggregator_rent, 22.35, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, 0.82, 'Не совпадает комисия банка')
        self.assertEquals(calc.earnings, 125.83, 'Не совпадает сумма пришедшая на фирму')
        self.assertEquals(calc.driver_salary, 48.24, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.assistance, 2.41, 'Не совпадает комисия фирмы')

        self.assertEquals(calc.investment_income, 48.23, 'Не совпадает прибыль машины')
        self.assertEquals(calc.car_income, 96.47, 'Деньги пришли на фирму')


    def test_from_xls(self):
        calc = TripCalculator(11.93, 170, 170,
                              15, 18.96, 4,
                              17, 17, 2.5, 0,
                              5, 50, 50)

        self.assertEquals(calc.cash, 170, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cash, 0, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.taxi_aggregator_rent, 28.90, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, -0.72, 'Не совпадает комисия банка')
        self.assertEquals(calc.assistance, 2.41, 'Не совпадает комисия фирмы')
        self.assertEquals(calc.fuel_compensation, 45.3, 'Не совпадает стоимость топлива')
        self.assertEquals(calc.driver_salary, 48.26, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.investment_income, 48.26, 'Не совпадает прибыль машины')
        self.assertEquals(calc.car_income, 96.52, 'Не совпадают фонд расчета прибыли')

    def test_from_xls_new(self):
        calc = TripCalculator(11.93, 170, 170,
                              15, 20, 4,
                              17, 17, 2.5, 0,
                              10, 50, 50)

        self.assertEquals(calc.cash, 170, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cash, 0, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.taxi_aggregator_rent, 28.90, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, -0.72, 'Не совпадает комисия банка')
        self.assertEquals(calc.assistance, 4.70, 'Не совпадает комисия фирмы')
        self.assertEquals(calc.fuel_compensation, 47.79, 'Не совпадает стоимость топлива')
        self.assertEquals(calc.driver_salary, 47.02, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.investment_income, 47.01, 'Не совпадает прибыль машины')
        # self.assertEquals(calc.real_amount, 96.52, 'Не совпадают фонд расчета прибыли')
        self.assertEquals(calc.earnings, 141.82, 'Деньги пришедшие от уклона')
        self.assertEquals(calc.investor_profit, 21.15)
        self.assertEquals(calc.firm_profit, 21.16)

    def test_from_xls_new_combo(self):
        calc = TripCalculator(8.28, 147, 77,
                              15, 20, 4,
                              17, 17, 2.5, 0,
                              10, 50, 50)

        self.assertEquals(calc.cash, 77, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cash, 70, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.taxi_aggregator_rent, 24.99, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, 1.13, 'Не совпадает комисия банка')
        self.assertEquals(calc.assistance, 4.2, 'Не совпадает assistance')
        self.assertEquals(calc.fuel_compensation, 36.84, 'Не совпадает стоимость топлива')
        self.assertEquals(calc.driver_salary, 42.02, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.investment_income, 42.02, 'Не совпадает прибыль машины')
        # self.assertEquals(calc.real_amount, 96.52, 'Не совпадают фонд расчета прибыли')
        self.assertEquals(calc.earnings, 120.88, 'Деньги пришедшие от уклона')
        self.assertEquals(calc.investor_profit, 18.91)
        self.assertEquals(calc.firm_profit, 18.91)


    def test_from_xls_new_credit(self):
        calc = TripCalculator(13.31, 137, 0,
                              15, 20, 4,
                              17, 17, 2.5, 0,
                              10, 50, 50)

        self.assertEquals(calc.cash, 0, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cash, 137, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.taxi_aggregator_rent, 23.29, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, 2.84, 'Не совпадает комисия банка')
        self.assertEquals(calc.assistance, 2.95, 'Не совпадает assistance')
        self.assertEquals(calc.fuel_compensation, 51.93, 'Не совпадает стоимость топлива')
        self.assertEquals(calc.driver_salary, 29.47, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.investment_income, 29.47, 'Не совпадает прибыль машины')
        # self.assertEquals(calc.real_amount, 96.52, 'Не совпадают фонд расчета прибыли')
        self.assertEquals(calc.earnings, 110.87, 'Деньги пришедшие от уклона')
        self.assertEquals(calc.investor_profit, 13.26)
        self.assertEquals(calc.firm_profit, 13.26)

    def test_from_code(self):
        calc = TripCalculator(9.49, 134, 0,
                              15, 18.98118, 4,
                              17, 17, 2.5, 0,
                              10, 50, 50)

        self.assertEquals(calc.cash, 0, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cash, 134, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.taxi_aggregator_rent, 22.78, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, 2.78, 'Не совпадает комисия банка')
        self.assertEquals(calc.fuel_compensation, 38.41, 'Не совпадает стоимость топлива')
        self.assertEquals(calc.earnings, 108.44, 'Деньги пришедшие от уклона')
        self.assertEquals(calc.car_income, 70.03, 'Не совпадают фонд расчета прибыли (сумма без топлива)')

        self.assertEquals(calc.driver_salary, 35.02, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.investment_income, 35.01, 'Не совпадает прибыль машины')
        self.assertEquals(calc.assistance, 3.5, 'Не совпадает assistance')
        self.assertEquals(calc.investor_profit, 15.75)
        self.assertEquals(calc.firm_profit, 15.76)

