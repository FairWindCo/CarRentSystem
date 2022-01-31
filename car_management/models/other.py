import math

from audit_log.models import CreatingUserField
from constance import config
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction, IntegrityError
# Create your models here.
from django.db.models import Q, F
from django.utils import timezone
from django.utils.datetime_safe import datetime

from balance.models import Account, Transaction, CashBox
from balance.services import Balance


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account = models.OneToOneField(Account, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'account'),)
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Провили пользователя'

    def __str__(self):
        return f'{self.user.username} {self.account.name}'
