from datetime import timedelta

from django.db import models

from car_management.models import TimeType


class StatisticsType(models.IntegerChoices):
    DONT_WORK = 0, 'Не вести статистику, машина отключена'
    TRIP_STAT = 1, 'Только статистика по поездкам'
    DAY_STAT = 2, 'Только статистика по дням'
    TRIP_DAY_PAID = 10, 'Статистика по поездкам и оплата по дням'
    TRIP_PAID_DAY = 20, 'Оплата по поездкам и статистика по дням'


class TransactionType(models.IntegerChoices):
    NO_TRANSACTION = 0, "Не заводить транзакции по поездкам"
    FULL_TRANSACTION = 1, "Детальное расписание операций"
    SIMPLE_TRANSACTION = 3, "Только корректировки баланса"


class RentPrice(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название тарифа')
    type_class = models.PositiveSmallIntegerField(choices=TimeType.choices,
                                                  verbose_name='Тип учета',
                                                  default=TimeType.DAYS)
    price = models.FloatField(verbose_name='Цена оренды в единицу времени', default=600)
    min_time = models.PositiveIntegerField(verbose_name='Минимальный срок аренды', default=3)
    safe_time = models.PositiveIntegerField(verbose_name='Срок аренды для расчета стоимости залога', default=7)

    replaced_by_new = models.ForeignKey('RentPrice', on_delete=models.CASCADE, blank=True, null=True)
    can_break_rent = models.BooleanField(verbose_name='Разрешен досочный возврат', default=True)
    trip_many_paid = models.BooleanField(verbose_name='Проведение оплат по поездкам', default=False)
    statistics_type = models.PositiveIntegerField(choices=StatisticsType.choices, default=StatisticsType.TRIP_DAY_PAID,
                                                  verbose_name='Тип собираемой статистики')
    paid_type = models.PositiveIntegerField(choices=TransactionType.choices, default=TransactionType.NO_TRANSACTION,
                                            verbose_name='Тип проводимых платежей')
    work_in_taxi = models.BooleanField(verbose_name='Работа в такси', default=False)

    def to_dict_m(self):
        return {
            'type_class': self.type_class,
            'price': self.price,
            'min_time': self.min_time,
            'safe_time': self.safe_time,
            'can_break_rent': self.can_break_rent,
            'trip_many_paid': self.trip_many_paid,
        }

    def from_dict_m(self, modif: dict):
        self.type_class = modif.get('type_class', None)
        self.price = modif.get('price', None)
        self.min_time = modif.get('min_time', None)
        self.safe_time = modif.get('safe_time', None)
        self.can_break_rent = modif.get('can_break_rent', None)
        self.trip_many_paid = modif.get('trip_many_paid', None)

    @classmethod
    def from_dict_compare_create(cls, initial, modif: dict, new_name_mod: str = ''):
        if initial is not None:
            init = initial.to_dict_m()
            if init == modif:
                return initial
            else:
                new_name_mod = initial.name + new_name_mod

        new_obj = cls(name=new_name_mod,
                      type_class=modif.get('type_class', None),
                      price=modif.get('price', None),
                      min_time=modif.get('min_time', None),
                      safe_time=modif.get('safe_time', None),
                      can_break_rent=modif.get('can_break_rent', None),
                      trip_many_paid=modif.get('trip_many_paid', None),
                      )
        new_obj.save()
        return new_obj

    def minimal(self):
        if self.type_class == TimeType.DAYS:
            return timedelta(days=self.min_time)
        else:
            return timedelta(seconds=self.min_time * 3600)

    def get_min_time(self):
        return timedelta(days=self.min_time) if self.type_class == TimeType.DAYS else timedelta(
            seconds=self.min_time * 3600)

    def get_safe_time(self):
        return timedelta(days=self.safe_time) if self.type_class == TimeType.DAYS else timedelta(
            seconds=self.safe_time * 3600)

    def calculate_time_interval(self, delta: timedelta, min_time):
        time = delta if delta > min_time else min_time
        return self.time_interval(time)

    def time_interval(self, delta: timedelta):
        if self.type_class == TimeType.DAYS:
            days = delta.days
            if delta.seconds > 0:
                days += 1
            return days
        else:
            hours = 24 * delta.days + int(delta.seconds / 3600)
            minutes = delta.seconds % 3600
            if minutes > 0:
                hours += 1
            return hours

    def calculate_price(self, price, delta: timedelta, min_time):
        interval = self.calculate_time_interval(delta, min_time)
        print('interval', interval)
        return interval * price

    def get_price(self, delta: timedelta):
        return self.calculate_price(self.price, delta, self.minimal())

    def get_return_price(self, start_time, plan_end_time, fact_end_time):
        if not self.can_break_rent:
            return False, 0
        if not self.work_in_taxi:
            return True, 0
        minimal = self.minimal()
        plan_delta = self.calculate_time_interval(plan_end_time - start_time, minimal)
        fact_delta = self.calculate_time_interval(fact_end_time - start_time, minimal)
        return (plan_delta - fact_delta) * self.price

    def get_deposit(self, delta: timedelta):
        if not delta or delta == 0:
            return self.price * self.safe_time
        return self.calculate_price(self.price, delta, self.get_safe_time())

    def clean(self):
        super().clean()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.pk is None:
            super().save(force_insert, force_update, using, update_fields)
        else:
            car_in_price = self.rent_price_cars.all()
            scheduled_price = self.scheduled_price.all()
            if scheduled_price:
                new_obj = RentPrice(name=self.name, safe_time=self.safe_time,
                                    type_class=self.type_class,
                                    price=self.price,
                                    min_time=self.min_time,
                                    replaced_by_new=None,
                                    can_break_rent=self.can_break_rent)
                new_obj.save()
                if self.replaced_by_new is None:
                    RentPrice.objects.filter(pk=self.pk).update(replaced_by_new=new_obj)
                if car_in_price:
                    car_in_price.update(rent_price_plan=new_obj)
            else:
                super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.name} ({"Активен" if self.replaced_by_new is None else "Заменен"})'

    class Meta:
        verbose_name = 'Тариф аренды'
        verbose_name_plural = 'Тарифы аренды'


class RentTerms(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название пакета условий')
    profit = models.FloatField(default=50, verbose_name='Процент распределения прибыли')
    fuel_compensation = models.FloatField(default=100, verbose_name='Процент компенсации топлива')
    additional_millage = models.PositiveIntegerField(verbose_name='Дополнительный километраж на поездку', default=4)
    min_trips = models.PositiveIntegerField(verbose_name='Минимальное количество поездок', default=3)
    max_millage = models.PositiveIntegerField(verbose_name='Макс км за интервал', default=2000)
    plan_amount = models.FloatField(verbose_name='План по кассе', default=2500)
    trips_control = models.BooleanField(verbose_name='Контроль за количеством поездок', default=True)
    millage_control = models.BooleanField(verbose_name='Контроль за километражем', default=True)
    amount_control = models.BooleanField(verbose_name='Контроль за суммой кассы', default=False)
    type_class = models.PositiveSmallIntegerField(choices=TimeType.choices,
                                                  verbose_name='Тип учета',
                                                  default=TimeType.DAYS)
    control_interval = models.PositiveIntegerField(verbose_name='Контрольный интервал', default=7)
    control_interval_paid_distance = models.PositiveIntegerField(verbose_name='Оплата за интервал', default=1)
    replaced_by_new = models.ForeignKey('RentTerms', on_delete=models.CASCADE, blank=True, null=True)

    def clean(self):
        super().clean()

    def to_dict_m(self):
        return {
            'profit': self.profit,
            'fuel_compensation': self.fuel_compensation,
            'additional_millage': self.additional_millage,
            'min_trips': self.min_trips,
            'max_millage': self.max_millage,
            'plan_amount': self.plan_amount,
            'trips_control': self.trips_control,
            'millage_control': self.millage_control,
            'amount_control': self.amount_control,
            'type_class': self.type_class,
            'control_interval': self.control_interval,
            'control_interval_paid_distance': self.control_interval_paid_distance,
        }

    def from_dict_m(self, modif: dict):
        self.profit = modif.get('profit', None)
        self.fuel_compensation = modif.get('fuel_compensation', None)
        self.additional_millage = modif.get('additional_millage', None)
        self.min_trips = modif.get('min_trips', None)
        self.max_millage = modif.get('max_millage', None)
        self.plan_amount = modif.get('plan_amount', None)

        self.trips_control = modif.get('trips_control', None)
        self.millage_control = modif.get('millage_control', None)
        self.amount_control = modif.get('amount_control', None)
        self.type_class = modif.get('type_class', None)
        self.control_interval = modif.get('control_interval', None)
        self.control_interval_paid_distance = modif.get('control_interval_paid_distance', None)

    @classmethod
    def from_dict_compare_create(cls, initial, modif: dict, new_name_mod: str = ''):
        if initial is not None:
            init = initial.to_dict_m()
            if init == modif:
                return initial
            else:
                new_name_mod = initial.name + new_name_mod

        new_obj = cls(name=new_name_mod,
                      profit=modif.get('profit', None),
                      fuel_compensation=modif.get('fuel_compensation', None),
                      additional_millage=modif.get('additional_millage', None),
                      min_trips=modif.get('min_trips', None),
                      max_millage=modif.get('max_millage', None),
                      plan_amount=modif.get('plan_amount', None),

                      trips_control=modif.get('trips_control', None),
                      millage_control=modif.get('millage_control', None),
                      amount_control=modif.get('amount_control', None),
                      type_class=modif.get('type_class', None),
                      control_interval=modif.get('control_interval', None),
                      control_interval_paid_distance=modif.get('control_interval_paid_distance', None),
                      )
        new_obj.save()
        return new_obj

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.pk is None:
            super().save(force_insert, force_update, using, update_fields)
        else:
            drivers_terms = self.drivers_terms.all()
            scheduled_price = self.scheduled_terms.all()
            if scheduled_price:
                new_obj = RentPrice(name=self.name,
                                    fuel_compensation=self.fuel_compensation,
                                    additional_millage=self.additional_millage,
                                    min_trips=self.min_trips,
                                    max_millage=self.max_millage,
                                    plan_amount=self.plan_amount,
                                    trips_control=self.trips_control,
                                    millage_control=self.millage_control,
                                    amount_control=self.amount_control,
                                    type_class=self.type_class,
                                    control_interval=self.control_interval,
                                    control_interval_paid_distance=self.control_interval_paid_distance,
                                    replaced_by_new=None,
                                    )
                new_obj.save()
                if self.replaced_by_new is None:
                    RentPrice.objects.filter(pk=self.pk).update(replaced_by_new=new_obj)
                if drivers_terms:
                    drivers_terms.update(default_terms=new_obj)
            else:
                super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.name} ({"Активен" if self.replaced_by_new is None else "Заменен"})'

    class Meta:
        verbose_name = 'Условия аренды'
        verbose_name_plural = 'Условия аренды'
