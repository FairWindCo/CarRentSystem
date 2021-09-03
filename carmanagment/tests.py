from django.test import TestCase

# Create your tests here.
from balance.services import Balance
from carmanagment.models import ExpensesTypes, Investor, CarBrand, CarModel, Counterpart
from carmanagment.services import ExpensesProcessor, CarCreator


class CheckExpense(TestCase):
    def setUp(self):
        self.brand = CarBrand(name='KIA')
        self.brand.save()
        self.model = CarModel(name='CEED', brand=self.brand)
        self.model.save()
        self.investor = Investor(name='test', profit=20)
        self.investor.save()
        self.expense_type = ExpensesTypes(name='Test CAR REPAIR',
                                          type_class=ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE)
        self.expense_type.save()
        self.expense_type2 = ExpensesTypes(name='Test REPAIR',
                                           type_class=ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE)
        self.expense_type2.save()
        self.counterpart = Counterpart(name='STO')
        self.counterpart.save()
        self.car = CarCreator.add_new_car(self.investor, self.model, 'AA1919OO', 2013, 100000, 10000)

    def test_expense_account_modification(self):
        # Car investment before capital repair
        self.assertEquals(Balance.get_current_balance(self.car.investment), -10000)
        expense = ExpensesProcessor.form_car_capital_expense(
            self.car, 27200, 27.2, self.expense_type, self.counterpart, 'REPAIR CAR ON STO'
        )
        self.assertEquals(expense.amount, 27200)
        # Car investment after capital repair
        self.assertEquals(Balance.get_current_balance(self.car.investment), -11000)
        self.assertEquals(Balance.get_current_balance(self.car.car_investor), -27200)
        self.assertEquals(Balance.get_current_balance(self.car), 0)

    def test_correct_expense_type(self):
        # Car investment before capital repair
        self.assertRaises(TypeError, ExpensesProcessor.form_car_capital_expense,
                          self.car, 27200, 27.2, self.expense_type2, self.counterpart, 'REPAIR CAR ON STO'
                          )
