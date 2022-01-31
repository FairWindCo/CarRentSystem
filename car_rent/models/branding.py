from balance.services import Balance
from constance import config
from django.db import models, transaction, IntegrityError
from django.utils.timezone import now

from car_management.models import Car


class BrandingAmount(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    stat_date = models.DateField(verbose_name='Дата', default=now())
    amount = models.FloatField(verbose_name='Доход от брендирования', default=0)
    operate = models.FloatField(verbose_name='Операционные затраты', default=14)
    investor_amount = models.FloatField(verbose_name='Прибыль инвестора', default=14)

    class Meta:
        verbose_name = 'Брендирование'
        verbose_name_plural = 'Брендирование'
        unique_together = (('car', 'stat_date'),)

    @classmethod
    def make_branding(cls, car, amount):
        branding = cls(car=car, amount=amount)
        branding.calculate()
        return branding

    def calculate(self):
        investor_percent = self.car.car_investor.profit / 100
        operating_percent = self.car.car_investor.operating_costs_percent / 100
        self.operate = operating_percent * self.amount
        self.investor_amount = investor_percent * (self.amount - self.operate)

        self.save()

    @property
    def firm_rent(self):
        return self.amount - self.investor_amount - self.operate

    def make_transaction(self, operator_cash_box):
        firm_account = config.FIRM
        Balance.form_transaction(Balance.DEPOSIT, [
            (None, operator_cash_box, round(self.amount * 100), 'Сумма за брендирование в кассу'),
            (None, self.car, round(self.amount * 100), 'Сумма за брендирование в кассу'),
            (self.car, firm_account, round(self.operate * 100), 'Комисия за обслуживание'),
            # (self.car, self.car.car_investor, round(self.investor_amount * 100), 'Прибыль за брендирование в кассу'),
            # (self.car, firm_account, round(self.firm_rent * 100), 'Прибыль за брендирование в кассу'),
        ], f'Доход за брендирование авто {self.car.name}')
