from datetime import timedelta

from django.db import models


class RentPrice(models.Model):

    class TimeType(models.IntegerChoices):
        HOUR = (1, 'Учет в часах')
        DAYS = (2, 'Учет в днях')

    name = models.CharField(max_length=100, verbose_name='Название тарифа')
    type_class = models.PositiveSmallIntegerField(choices=TimeType.choices,
                                                  verbose_name='Тип учета',
                                                  default=TimeType.DAYS)
    price = models.FloatField(verbose_name='Цена оренды в единицу времени', default=600)
    min_time = models.PositiveIntegerField(verbose_name='Минимальный срок аренды', default=3)
    safe_time = models.PositiveIntegerField(verbose_name='Срок аренды для расчета стоимости залога', default=7)
    replaced_by_new = models.ForeignKey('RentPrice', on_delete=models.CASCADE, blank=True, null=True)
    can_break_rent = models.BooleanField(verbose_name='Разрешен досочный возврат', default=True)

    def minimal(self):
        if self.type_class == self.TimeType.DAYS:
            return timedelta(days=self.min_time)
        else:
            return timedelta(seconds=self.min_time * 3600)

    def get_min_time(self):
        return timedelta(days=self.min_time) if self.type_class == self.TimeType.DAYS else timedelta(
            seconds=self.min_time * 3600)

    def get_safe_time(self):
        return timedelta(days=self.safe_time) if self.type_class == self.TimeType.DAYS else timedelta(
            seconds=self.safe_time * 3600)

    def calculate_time_interval(self, delta: timedelta, min_time):
        time = delta if delta > min_time else min_time
        return self.time_interval(time)

    def time_interval(self, delta: timedelta):
        if self.type_class == self.TimeType.DAYS:
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
        minimal = self.minimal()
        plan_delta = self.calculate_time_interval(plan_end_time - start_time, minimal)
        fact_delta = self.calculate_time_interval(fact_end_time - start_time, minimal)
        return (plan_delta - fact_delta) * self.price

    def get_deposit(self, delta: timedelta):
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
        return f'{self.name} действует: {self.replaced_by_new is None}'

    class Meta:
        verbose_name = 'Тариф аренды'
        verbose_name_plural = 'Тарифы аренды'