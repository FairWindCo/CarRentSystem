from constance import config
from django.utils.translation import gettext_lazy as _

from carmanagment.custom_admin import CustomModelPage
from carmanagment.models import *
from carmanagment.serivices.car_rent_service import CarRentService
from carmanagment.serivices.car_service import CarCreator
from carmanagment.serivices.expense_service import ExpensesProcessor
from external_services.fresh_contants import get_special_fuel_help_text


class CarAddPage(CustomModelPage):
    title = 'Подключить авто'  # set page title
    # Define some fields.
    car_plate = models.CharField(max_length=100, verbose_name='номе машины')
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, verbose_name='Ивестор')
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, verbose_name='Модель')
    year = models.PositiveIntegerField(verbose_name='Год выпуска', validators=[
        MaxValueValidator(2100),
        MinValueValidator(1900)
    ])
    millage = models.PositiveIntegerField(verbose_name='Пробег на текущий момент')
    amount = models.PositiveIntegerField(verbose_name='Сумма инвестиций')

    def clean(self):
        if not hasattr(self, 'investor') or self.investor is None:
            raise ValidationError(_('Ивестор обязателен'))
        if not hasattr(self, 'car_model') or self.car_model is None:
            raise ValidationError(_('Модель обязательна'))
        super().clean()

    def save(self):
        CarCreator.add_new_car(self.investor, self.car_model, self.car_plate, self.year, self.millage, self.amount)
        self.bound_admin.message_success(self.bound_request, _('Машина подключена'))


class ExpensePage(CustomModelPage):
    title = 'Внести "затрату" по машине'  # set page title
    # Define some fields.
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Авто')
    expense_type = models.ForeignKey(ExpensesTypes, on_delete=models.CASCADE, verbose_name='Тип затраты')
    amount = models.PositiveIntegerField(verbose_name='Сумма')
    counterpart = models.ForeignKey(Counterpart, on_delete=models.CASCADE, verbose_name='Контрагент')
    comment = models.TextField(verbose_name='Коментарий')
    currency_rate = models.FloatField(verbose_name='Курс', null=True, blank=True, default=config.USD_CURRENCY)

    def clean(self):
        if not hasattr(self, 'expense_type') or self.expense_type is None:
            raise ValidationError(_('Тип затьраты обязателен'))
        if self.expense_type.type_class not in [ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE,
                                                ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE,
                                                ExpensesTypes.ExpensesTypesClassify.CRASH_CAR_EXPENSE,
                                                ]:
            raise ValidationError(_('Не верный класс затраты для машины'))
        if self.expense_type.type_class == ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE and self.currency_rate is None:
            raise ValidationError(_('Для капитальных затрат курс - обязателен'))
        if self.expense_type.type_class == ExpensesTypes.ExpensesTypesClassify.CRASH_CAR_EXPENSE and self.currency_rate is None:
            raise ValidationError(_('Для страховых затрат курс - обязателен'))
        super().clean()

    def save(self):
        if not hasattr(self, 'expense_type'):
            raise ValidationError(_('Тип затраты обязателен'))
        if self.expense_type.type_class in [ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE,
                                            ExpensesTypes.ExpensesTypesClassify.CRASH_CAR_EXPENSE]:
            ExpensesProcessor.form_car_capital_expense(
                self.car, self.amount, self.currency_rate, self.expense_type, self.counterpart, self.comment)
        elif self.expense_type.type_class == ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE:
            ExpensesProcessor.form_car_current_expense(self.car, self.amount, self.expense_type,
                                                       self.counterpart, self.comment)
            self.bound_admin.message_success(self.bound_request, _('Затрата добавлена'))
        else:
            raise ValidationError(_('Не верный класс затраты для машины'))


class OtherExpensePage(CustomModelPage):
    title = 'Внести "затрату"'  # set page title
    # Define some fields.
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Аккаунт')
    expense_type = models.ForeignKey(ExpensesTypes, on_delete=models.CASCADE, verbose_name='Тип затраты')
    amount = models.PositiveIntegerField(verbose_name='Сумма')
    counterpart = models.ForeignKey(Counterpart, on_delete=models.CASCADE, verbose_name='Контрагент',
                                    related_name='other_expense')
    comment = models.TextField(verbose_name='Коментарий')

    def clean(self):
        if not hasattr(self, 'expense_type'):
            raise ValidationError(_('Тип затраты обязателен'))
        if not hasattr(self, 'account'):
            raise ValidationError(_('Аккаунт обязателен'))
        if self.expense_type.type_class == ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE or \
                self.expense_type.type_class == ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE or \
                isinstance(self.account, Car) or self.account.car is not None:
            raise ValidationError(_('Затраты для машины - заносятся отдельно'))
        if self.account.currency == Account.AccountCurrency.DOLLAR:
            raise ValidationError(_('Внос капитальных затрат не разрешен'))
        super().clean()

    def save(self):
        if self.expense_type is None:
            raise ValidationError(_('Тип затьраты обязателен'))
        if self.expense_type.type_class == ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE or \
                self.expense_type.type_class == ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE:
            raise ValidationError(_('Затраты для машины - заносятся отдельно'))
        else:
            ExpensesProcessor.form_expense(self.account, self.amount, self.expense_type,
                                           self.counterpart, self.comment)
            self.bound_admin.message_success(self.bound_request, _('Затрата добавлена'))


class TaxiTripPage(CustomModelPage):
    title = 'Добавить поездку в Такси'  # set page title
    # Define some fields.
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Авто', related_name='taxi_car')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name='Водитель', related_name='taxi_driver')
    counterpart = models.ForeignKey(TaxiOperator, on_delete=models.CASCADE, verbose_name='Контрагент',
                                    related_name='taxi_service')
    amount = models.PositiveIntegerField(verbose_name='Сумма')
    millage = models.PositiveIntegerField(verbose_name='Растояние')
    gas_price = models.PositiveIntegerField(verbose_name='Цена газа', help_text=get_special_fuel_help_text())
    cash = models.BooleanField(verbose_name='Оплата наличными', default=False)
    start_time = models.DateTimeField(verbose_name='Дата и время начала поездки')

    def clean(self):
        if not hasattr(self, 'car'):
            raise ValidationError(_('Машина обязательна'))
        if not hasattr(self, 'driver'):
            raise ValidationError(_('Водительн обязателен'))
        if not hasattr(self, 'counterpart'):
            raise ValidationError(_('Контрагент обязателен'))
        super().clean()

    def save(self):
        if TaxiTrip.manual_create_taxi_trip(self.car, self.driver, self.start_time,
                                            self.counterpart, self.millage, self.amount,
                                            self.gas_price, self.cash):
            self.bound_admin.message_success(self.bound_request, _('Поездка добавлена'))


class EmptyModel(CustomModelPage):
    pass


class CarRentPage(CustomModelPage):
    title = 'Вывод прибыли по машине'  # set page title
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Модель')
    amount = models.FloatField(verbose_name='Сумма', validators=[
        MinValueValidator(0.01)
    ])

    def clean(self):
        if not hasattr(self, 'car') or self.car is None:
            raise ValidationError(_('Машина обязательна'))
        super().clean()

    def save(self):
        if not self.bound_request.user and not hasattr(self.bound_request.user, 'userprofile'):
            raise ValidationError(_('Пользователь не можут списывать прибыли'))
        firm_account = self.bound_request.user.userprofile.account
        result, message = CarRentService.move_rent_many(self.car, self.amount, firm_account)
        if result:
            self.bound_admin.message_success(self.bound_request, _('прибыль списана'))
        else:
            self.bound_admin.message_error(self.bound_request, message)
