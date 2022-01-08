from constance import config
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from balance.models import CashBox, Account

from django_helpers.admin import CustomModelPage
from django_helpers.admin.artificial_admin_models import CustomPageModelAdmin
from carmanagment.models import ExpensesTypes, Car, Counterpart
from carmanagment.serivices.expense_service import ExpensesProcessor


class CarExpenseBase(CustomPageModelAdmin):
    autocomplete_fields = ('car', 'expense_type', 'counterpart')


class OtherExpenseBase(CustomPageModelAdmin):
    autocomplete_fields = ('account', 'expense_type', 'counterpart')


class ExpensesTypesAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

    def get_search_results(self, request, queryset, search_term):
        print("In get search results", request)
        if 'model_name' in request.GET:
            if request.GET['model_name'] == 'expensepage':
                queryset = queryset.filter(Q(type_class=ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE) | Q(
                    type_class=ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE))
            elif request.GET['model_name'] == 'otherexpensepage':
                queryset = queryset.exclude(Q(type_class=ExpensesTypes.ExpensesTypesClassify.CAR_EXPENSE) | Q(
                    type_class=ExpensesTypes.ExpensesTypesClassify.CAPITAL_CAR_EXPENSE))
        results = super().get_search_results(request, queryset, search_term)
        return results


class ExpensePage(CustomModelPage):
    title = 'Внести "затрату" по машине'  # set page title
    # Define some fields.
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Авто')
    expense_type = models.ForeignKey(ExpensesTypes, on_delete=models.CASCADE, verbose_name='Тип затраты')
    amount = models.PositiveIntegerField(verbose_name='Сумма')
    counterpart = models.ForeignKey(Counterpart, on_delete=models.CASCADE, verbose_name='Контрагент')
    comment = models.TextField(verbose_name='Коментарий')
    currency_rate = models.FloatField(verbose_name='Курс', null=True, blank=True, default=config.USD_CURRENCY)
    cash_box = models.ForeignKey(CashBox, on_delete=models.CASCADE, verbose_name='Касса',
                                 related_name='expense_cash_box')

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
        if self.cash_box.current_balance() <= self.amount:
            raise ValidationError(_('В кассе недостаточно денег'))
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
    cash_box = models.ForeignKey(CashBox, on_delete=models.CASCADE, verbose_name='Касса',
                                 related_name='other_expense_cash_box')

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
        if self.cash_box.current_balance() <= self.amount:
            raise ValidationError(_('В кассе недостаточно денег'))
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