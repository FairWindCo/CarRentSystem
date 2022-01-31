from django.db import models


class TimeType(models.IntegerChoices):
    HOUR = (1, 'Учет в часах')
    DAYS = (2, 'Учет в днях')
    WEEK = (3, 'Учет в неделях')
    MONTH = (4, 'Учет в месяцах')
