from django.contrib.auth.models import User
from django.db import models

from balance.models import Account


# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    can_confirm_as_manager = models.BooleanField(default=False, verbose_name='Может подтверждать как менеджер')
    can_confirm_as_investor = models.BooleanField(default=False, verbose_name='Может подтверждать как инвестор')

    class Meta:
        unique_together = (('user', 'account'),)
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователя'

    def __str__(self):
        return f'{self.user.username} {self.account.name}'
