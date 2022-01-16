from django.test import TestCase

from carmanagment.models.taxioperatorcalculator import TaxiCalculator


class CheckTaxiCaclculator(TestCase):
    def test_only_credit_cart_cash_trip(self):
        calc = TaxiCalculator(4.49, 82, 0,
                              14, 19.0476470588235, 4,
                              15, 15, 2.5,
                              5, 50)

        self.assertEquals(calc.cash, 0, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cart_cash, 82, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.payer_interest, 12.3, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, 1.74, 'Не совпадает комисия банка')
        self.assertEquals(calc.operating_costs, 3.4, 'Не совпадает комисия фирмы')
        self.assertEquals(calc.driver_money, 22.66, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.car_profit, 19.26, 'Не совпадает прибыль машины')
        self.assertEquals(calc.real_amount, 45.32, 'Деньги пришли на фирму')

    def test_only_cash_trip(self):
        calc = TaxiCalculator(3.18, 80, 80,
                              14, 19.0476470588235, 4,
                              15, 15, 2.5,
                              5, 50)

        self.assertEquals(calc.cash, 80, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cart_cash, 0, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.payer_interest, 12, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, -0.3, 'Не совпадает комисия банка')
        self.assertEquals(calc.operating_costs, 3.42, 'Не совпадает комисия фирмы')
        self.assertEquals(calc.driver_money, 24.58, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.car_profit, 21.16, 'Не совпадает прибыль машины')
        self.assertEquals(calc.real_amount, 49.15, 'Деньги пришли на фирму')

    def test_mix_cash_trip(self):
        calc = TaxiCalculator(7.01, 149, 94,
                              14, 19.0476470588235, 4,
                              15, 15, 2.5,
                              5, 50)

        self.assertEquals(calc.cash, 94, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cart_cash, 55, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.payer_interest, 22.35, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, 0.82, 'Не совпадает комисия банка')
        self.assertEquals(calc.trip_firm_total_many, 126.65, 'Не совпадает сумма пришедшая на фирму')
        self.assertEquals(calc.operating_costs, 6.29, 'Не совпадает комисия фирмы')
        self.assertEquals(calc.driver_money, 48.24, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.car_profit, 41.95, 'Не совпадает прибыль машины')
        self.assertEquals(calc.real_amount, 96.47, 'Деньги пришли на фирму')


    def test_from_xls(self):
        calc = TaxiCalculator(11.93, 170, 170,
                              15, 18.96, 4,
                              17, 17, 2.5,
                              5, 50, 50)

        self.assertEquals(calc.cash, 170, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cart_cash, 0, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.payer_interest, 28.90, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, -0.72, 'Не совпадает комисия банка')
        self.assertEquals(calc.operating_costs, 7.09, 'Не совпадает комисия фирмы')
        self.assertEquals(calc.fuel_compensation, 45.3, 'Не совпадает стоимость топлива')
        self.assertEquals(calc.driver_money, 48.26, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.car_profit, 41.17, 'Не совпадает прибыль машины')
        self.assertEquals(calc.real_amount, 96.52, 'Не совпадают фонд расчета прибыли')

    def test_from_xls_new(self):
        calc = TaxiCalculator(11.93, 170, 170,
                              15, 20, 4,
                              17, 17, 2.5,
                              10, 50, 50)

        self.assertEquals(calc.cash, 170, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cart_cash, 0, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.payer_interest, 28.90, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, -0.72, 'Не совпадает комисия банка')
        self.assertEquals(calc.operating_costs, 14.18, 'Не совпадает комисия фирмы')
        self.assertEquals(calc.fuel_compensation, 47.79, 'Не совпадает стоимость топлива')
        self.assertEquals(calc.driver_money, 47.02, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.car_profit, 32.83, 'Не совпадает прибыль машины')
        # self.assertEquals(calc.real_amount, 96.52, 'Не совпадают фонд расчета прибыли')
        self.assertEquals(calc.trip_many_without_bank, 141.82, 'Деньги пришедшие от уклона')
        self.assertEquals(calc.investor_profit, 16.42)
        self.assertEquals(calc.firm_profit, 16.42)

    def test_from_xls_new_combo(self):
        calc = TaxiCalculator(8.28, 147, 77,
                              15, 20, 4,
                              17, 17, 2.5,
                              10, 50, 50)

        self.assertEquals(calc.cash, 77, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cart_cash, 70, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.payer_interest, 24.99, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, 1.13, 'Не совпадает комисия банка')
        self.assertEquals(calc.operating_costs, 12.09, 'Не совпадает assistance')
        self.assertEquals(calc.fuel_compensation, 36.84, 'Не совпадает стоимость топлива')
        self.assertEquals(calc.driver_money, 42.02, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.car_profit, 29.93, 'Не совпадает прибыль машины')
        # self.assertEquals(calc.real_amount, 96.52, 'Не совпадают фонд расчета прибыли')
        self.assertEquals(calc.trip_many_without_bank, 120.88, 'Деньги пришедшие от уклона')
        self.assertEquals(calc.investor_profit, 14.97)
        self.assertEquals(calc.firm_profit, 14.97)


    def test_from_xls_new_credit(self):
        calc = TaxiCalculator(13.31, 137, 0,
                              15, 20, 4,
                              17, 17, 2.5,
                              10, 50, 50)

        self.assertEquals(calc.cash, 0, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cart_cash, 137, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.payer_interest, 23.29, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, 2.84, 'Не совпадает комисия банка')
        self.assertEquals(calc.operating_costs, 11.09, 'Не совпадает assistance')
        self.assertEquals(calc.fuel_compensation, 51.93, 'Не совпадает стоимость топлива')
        self.assertEquals(calc.driver_money, 29.47, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.car_profit, 18.38, 'Не совпадает прибыль машины')
        # self.assertEquals(calc.real_amount, 96.52, 'Не совпадают фонд расчета прибыли')
        self.assertEquals(calc.trip_many_without_bank, 110.87, 'Деньги пришедшие от уклона')
        self.assertEquals(calc.investor_profit, 9.19)
        self.assertEquals(calc.firm_profit, 9.19)

    def test_from_code(self):
        calc = TaxiCalculator(9.49, 134, 0,
                              15, 18.98118, 4,
                              17, 17, 2.5,
                              10, 50, 50)

        self.assertEquals(calc.cash, 0, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cart_cash, 134, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.payer_interest, 22.78, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, 2.78, 'Не совпадает комисия банка')
        self.assertEquals(calc.operating_costs, 10.84, 'Не совпадает assistance')
        self.assertEquals(calc.fuel_compensation, 38.41, 'Не совпадает стоимость топлива')
        self.assertEquals(calc.driver_money, 35.02, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.car_profit, 24.17, 'Не совпадает прибыль машины')
        # self.assertEquals(calc.real_amount, 96.52, 'Не совпадают фонд расчета прибыли')
        self.assertEquals(calc.trip_many_without_bank, 108.44, 'Деньги пришедшие от уклона')
        self.assertEquals(calc.investor_profit, 12.09)
        self.assertEquals(calc.firm_profit, 12.09)

