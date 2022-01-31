import datetime

from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.db import models
from django.db.models import Q, F, Sum
from balance.services import Balance
from car_management.models.cars import Car
from constance import config
from car_management.utils import get_sum


class CarSummaryStatistics(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='statistics')
    stat_date = models.DateField(verbose_name='Дата', default=now())
    stat_interval = models.PositiveIntegerField(verbose_name='Интервал', default=86400)
    gps_mileage = models.FloatField(verbose_name='Пробег по трекеру', default=0)
    taxi_mileage = models.FloatField(verbose_name='Пробег по оператору такси', default=0)
    taxi_trip_count = models.PositiveIntegerField(verbose_name='Кол-во поездок в такси', default=0)
    branding_amount = models.FloatField(verbose_name='Доход за брендирование', default=0)
    taxi_amount = models.FloatField(verbose_name='Доход от таксопарка', default=0)
    rent_amount = models.FloatField(verbose_name='Доход от аренды', default=0)
    expense = models.FloatField(verbose_name='Расходы', default=0)
    capital_expense = models.FloatField(verbose_name='Капитальные расходы', default=0)
    operate = models.FloatField(verbose_name='Операционные затраты', default=0)
    investor_amount = models.FloatField(verbose_name='Прибыль инвестора', default=0)
    driver_amount = models.FloatField(verbose_name='Зарплата водителя', default=0)
    # Логика следующая каждые н-ней сроится сумарный отчет за эти дни
    # он отмечается как требующий оплату в этот период никакие другие отчеты требующие оплату не допускаются
    report_paid = models.DateField(verbose_name='Дата оплаты по отчету', blank=True, null=True)
    plan_for_paid = models.BooleanField(verbose_name='Отчет требует оплаты', default=False)

    def validate_unique(self, exclude=None):
        result = super().validate_unique(exclude)
        current_report_date = self.stat_date
        if self.objects.annotate(start_interval=F('stat_date') - F('stat_interval')).filter(Q(
                start_interval__lte=current_report_date,
                stat_date__gte=current_report_date
        )).exists():
            raise ValidationError('Report for paid already exists!')

        return result

    @classmethod
    def build_summary_report(cls, car, report_date=now(), interval=7, need_paid=False):
        if report_date is None:
            report_date = now()
        report_date = (report_date.date() if isinstance(report_date, datetime.datetime) else report_date)
        report_start = report_date - datetime.timedelta(days=interval)

        query = cls.objects.filter(car=car, stat_date__lte=report_start, stat_date__gte=report_date,
                                   stat_interval=86400)

        stat_sum = query.aggregate(Sum('expense'),
                                   Sum('capital_expense'),
                                   Sum('gps_mileage'),
                                   Sum('taxi_mileage'),
                                   Sum('taxi_trip_count'),
                                   Sum('branding_amount'),
                                   Sum('taxi_amount'),
                                   Sum('rent_amount'),
                                   Sum('driver_amount'),
                                   Sum('operate'),
                                   Sum('investor_amount'),
                                   )
        report = cls(car=car, stat_date=report_date, interval=interval * 86400)
        report.expense = get_sum(stat_sum, 'expense__sum')
        report.capital_expense = get_sum(stat_sum, 'capital_expense__sum')
        report.gps_mileage = get_sum(stat_sum, 'gps_mileage__sum')
        report.taxi_mileage = get_sum(stat_sum, 'taxi_mileage__sum')
        report.taxi_trip_count = get_sum(stat_sum, 'taxi_trip_count__sum')
        report.branding_amount = get_sum(stat_sum, 'branding_amount__sum')
        report.taxi_amount = get_sum(stat_sum, 'taxi_amount__sum')
        report.rent_amount = get_sum(stat_sum, 'rent_amount__sum')
        report.driver_amount = get_sum(stat_sum, 'driver_amount__sum')
        report.operate = get_sum(stat_sum, 'operate__sum')
        report.investor_amount = get_sum(stat_sum, 'investor_amount__sum')
        report.plan_for_paid = need_paid
        report.save()

        last_report = cls.get_last_report_for_paid(car, report_start)
        if last_report:
            end_reported_period = last_report.stat_date + datetime.timedelta(seconds=last_report.stat_interval)
            plan_before_report = report_start - datetime.timedelta(days=1)
            if end_reported_period < plan_before_report:
                delta_period = (plan_before_report - end_reported_period).total_seconds()
                cls.build_summary_report(car, plan_before_report, int(delta_period))

    @classmethod
    def get_last_report_for_paid(cls, car, on_date=now()):
        if on_date is None:
            on_date = now()
        report_date = (on_date.date() if isinstance(on_date, datetime.datetime) else on_date)
        try:
            return cls.objects.filter(car=car, stat_date__gte=report_date,
                                      stat_interval__lte=86400,
                                      plan_for_paid=True).order_by('stat_date').first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_not_paid_report_before_date(cls, car, on_date=now()):
        if on_date is None:
            on_date = now()
        report_date = (on_date.date() if isinstance(on_date, datetime.datetime) else on_date)
        try:
            return cls.objects.filter(car=car, stat_date__gt=report_date,
                                      stat_interval__lte=86400, report_paid__isnull=True,
                                      plan_for_paid=True).order_by('stat_date').all()
        except cls.DoesNotExist:
            return []

    @classmethod
    def form_paid_operations(cls, car, on_date=now()):
        firm_account = config.FIRM
        if firm_account is None:
            raise ValueError('Need Set Firm account in Config')
        reports_for_paid = cls.get_not_paid_report_before_date(car, on_date)

        for report in reports_for_paid:
            operations = [
                (car, car.car_investor, round(report.investor_amount * 100), f'Прибыль инвестора за машину {car.name}'),
                (car, car.firm_account, round(report.firm_amount * 100), f'Прибыль компании за машину {car.name}'),
            ]
            if report.expense - report.capital_expense > 0:
                expense = round((report.expense - report.capital_expense) * 100)
                investor_part = round(expense * car.car_investor.profit)
                firm_part = expense - investor_part
                operations.append((car.car_investor, car, investor_part,
                                   f'Часть затрат инвестора за машину {car.name}'), )
                operations.append((firm_account, car, firm_part,
                                   f'Часть затрат фирмы за машину {car.name}'), )

            result = Balance.form_transaction(
                Balance.WITHDRAWAL,
                operations,
                f'Вывод прибыли за отчет {report.stat_date}'
            )
            if result:
                report.report_paid = on_date
                report.save()

    @property
    def firm_amount(self):
        return self.taxi_amount - self.driver_amount - self.investor_amount

    class Meta:
        unique_together = (('car', 'stat_date', 'stat_interval'),)
        verbose_name = 'Статистика по Авто'
        verbose_name_plural = 'Статистика по Авто'
