from abc import abstractmethod

from django.db import models
from django.utils.timezone import now


class TimeRange(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        abstract = True

    @abstractmethod
    def get_unique_check_in_range(self):
        pass

    def clean(self):
        from django.core.exceptions import ValidationError
        from django.db.models import Q
        current_time = now()
        if self.end_time is None or self.start_time is None:
            raise ValidationError('Start Date and end date is required')
        if self.end_time <= self.start_time:
            raise ValidationError('Start date need be less then End date')
        if self.end_time < current_time or self.start_time < current_time:
            raise ValidationError('Нельзя захватить прошлые периоды')

        if self.get_unique_check_in_range().filter(
                Q(start_time__lte=self.start_time, end_time__gte=self.start_time) |
                Q(start_time__lte=self.end_time, end_time__gte=self.end_time)
        ).exists():
            raise ValidationError('Такой объект уже есть')