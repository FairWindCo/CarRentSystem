from django.test import TestCase

from carmanagment.models.taxioperatorcalculator import TaxiCalculator


class CheckTaxiCaclculator(TestCase):
    def test_only_credit_cart_cash_trip(self):
        calc = TaxiCalculator(4.49, 82, 0,
                              14, 19.0476470588235, 4,
                              0.15, 0.15, 0.025,
                              5, 50)

        self.assertEquals(calc.cash, 0, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cart_cash, 82, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.payer_interest, 12.3, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, 1.74, 'Не совпадает комисия банка')
        self.assertEquals(calc.operating_costs, 3.4, 'Не совпадает комисия фирмы')
        self.assertEquals(calc.driver_money, 22.66, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.firm_profit, 19.26, 'Не совпадает прибыль машины')
        self.assertEquals(calc.real_amount, 45.32, 'Деньги пришли на фирму')

    def test_only_cash_trip(self):
        calc = TaxiCalculator(3.18, 80, 80,
                              14, 19.0476470588235, 4,
                              0.15, 0.15, 0.025,
                              5, 50)

        self.assertEquals(calc.cash, 80, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cart_cash, 0, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.payer_interest, 12, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, -0.3, 'Не совпадает комисия банка')
        self.assertEquals(calc.operating_costs, 3.42, 'Не совпадает комисия фирмы')
        self.assertEquals(calc.driver_money, 24.58, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.firm_profit, 21.16, 'Не совпадает прибыль машины')
        self.assertEquals(calc.real_amount, 49.15, 'Деньги пришли на фирму')

    def test_mix_cash_trip(self):
        calc = TaxiCalculator(7.01, 149, 94,
                              14, 19.0476470588235, 4,
                              0.15, 0.15, 0.025,
                              5, 50)

        self.assertEquals(calc.cash, 94, 'Наличики в поездке нет')
        self.assertEquals(calc.credit_cart_cash, 55, 'Не совпадает сумма по кредитной карте')
        self.assertEquals(calc.payer_interest, 22.35, 'Не совпадает процент по Уклону')
        self.assertEquals(calc.bank_rent, 0.82, 'Не совпадает комисия банка')
        self.assertEquals(calc.operating_costs, 6.29, 'Не совпадает комисия фирмы')
        self.assertEquals(calc.driver_money, 48.24, 'Не совпадает зарплата водителя')
        self.assertEquals(calc.firm_profit, 41.95, 'Не совпадает прибыль машины')
        self.assertEquals(calc.real_amount, 96.47, 'Деньги пришли на фирму')