from datetime import timedelta

from django.db import models, IntegrityError
from django.utils.timezone import now

from carmanagment.models import Car, Driver
from carmanagment.serivices.driver_search import get_car_current_driver


class WialonTrip(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start = models.DateTimeField(verbose_name='Дата начала поездки', default=now())
    end = models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения поездки')
    mileage = models.FloatField(verbose_name='Пробег по трекеру', default=0)
    fuel = models.PositiveIntegerField(verbose_name='Раход по трекеру', default=0)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='Водитель, если известно')
    avg_speed = models.PositiveIntegerField(verbose_name='Средняя скорость', default=0)
    max_speed = models.PositiveIntegerField(verbose_name='Максимальная скорость', default=0)

    @classmethod
    def construct_from_rows(cls, rows, car):
        for row in rows:
            cls.construct_from_dict(row, car)

    @classmethod
    def construct_from_dict(cls, data_dict, car):
        # 'num': row[0],
        # 'start_time': datetime.datetime.fromtimestamp(row[1]['v']).astimezone(LOCAL_TIMEZONE),
        # 'start_position': (float(row[2]['y']), float(row[2]['x'])),
        # 'end_time': datetime.datetime.fromtimestamp(row[3]['v']).astimezone(LOCAL_TIMEZONE),
        # 'end_position': (float(row[4]['y']), float(row[4]['x'])),
        # 'time': construct_delta_time(row[5]),
        # 'millage': float(row[6][:-3]),
        # 'avg_speed': int(row[9][:-5]),
        # 'max_speed': int(row[10]['t'][:-5]),
        # 'max_speed_point': (float(row[10]['x']), float(row[10]['y']))
        if car:
            timing: timedelta = data_dict['time']
            if timing.total_seconds() > 0:
                start_time = data_dict['start_time']
                driver = get_car_current_driver(car, start_time)
                try:
                    trip = cls(car=car, start=start_time, driver=driver,
                               end=data_dict['end_time'],
                               mileage=data_dict['millage'],
                               max_speed=data_dict['max_speed'],
                               avg_speed=data_dict['avg_speed']
                               )
                    trip.save()
                except IntegrityError:
                    trip = cls.objects.get(car=car, start=start_time)
                    trip.driver = driver
                    trip.end = data_dict['end_time']
                    trip.mileage = data_dict['millage']
                    trip.max_speed = data_dict['max_speed']
                    trip.avg_speed = data_dict['avg_speed']
                    trip.save()
    class Meta:
        verbose_name = 'GPS поездки'
        unique_together = (('car', 'start'),)


class WialonDayStat(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    stat_date = models.DateField(verbose_name='Дата', default=now())
    stat_interval = models.PositiveIntegerField(verbose_name='Интервал', default=0)
    mileage = models.FloatField(verbose_name='Пробег по трекеру', default=0)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='Водитель, если известно')
    stop_count = models.PositiveIntegerField(verbose_name='Остановок', default=0)
    park_count = models.PositiveIntegerField(verbose_name='Парковок', default=0)
    drive_time = models.PositiveIntegerField(verbose_name='Время поездки', default=0)
    park_time = models.PositiveIntegerField(verbose_name='Время стоянки', default=0)
    avg_speed = models.PositiveIntegerField(verbose_name='Средняя скорость', default=0)
    max_speed = models.PositiveIntegerField(verbose_name='Максимальная скорость', default=0)

    @classmethod
    def construct_from_dict(cls, stat, car):
        # 'report_name': data[0][1],
        # 'object_name': data[1][1],
        # 'start_interval': datetime.datetime.strptime(data[2][1], "%Y-%m-%d %H:%M:%S").astimezone(LOCAL_TIMEZONE),
        # 'end_interval': datetime.datetime.strptime(data[3][1], "%Y-%m-%d %H:%M:%S").astimezone(LOCAL_TIMEZONE),
        # 'count_stops': int(data[4][1]),
        # 'move_time': construct_delta_time(data[5][1]),
        # 'millage': int(data[6][1][:-3]),
        # 'avg_speed': int(data[9][1][:-5]),
        # 'max_speed': int(data[10][1][:-5]),
        # 'stop_time': construct_delta_time(data[13][1]),
        # 'parking_count': int(data[14][1]),
        if car:
            start_time = stat['start_interval']
            end_time = stat['end_interval']
            interval = int((end_time - start_time).total_seconds())
            driver = get_car_current_driver(car, start_time)
            try:
                print(start_time, interval, car)
                wialon_stat = cls(stat_date=start_time.date(),
                                  stat_interval=interval,
                                  car=car)
                wialon_stat.save()
            except IntegrityError:
                print(start_time, interval, car)
                wialon_stat = cls.objects.get(stat_date=start_time.date(),
                                              stat_interval=interval,
                                              car=car)
            wialon_stat.driver = driver
            wialon_stat.mileage = stat['millage']
            wialon_stat.park_count = stat['parking_count']
            wialon_stat.stop_count = stat['count_stops']
            wialon_stat.drive_time = (stat['move_time']).total_seconds()
            wialon_stat.park_time = (stat['stop_time']).total_seconds()
            wialon_stat.avg_speed = stat['avg_speed']
            wialon_stat.max_speed = stat['max_speed']
            wialon_stat.save()

    class Meta:
        verbose_name = 'GPS поездки'
        unique_together = (('car', 'stat_date', 'stat_interval'),)
