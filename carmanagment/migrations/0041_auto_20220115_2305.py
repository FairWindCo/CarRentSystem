# Generated by Django 3.2.6 on 2022-01-15 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carmanagment', '0040_auto_20220115_1944'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='wialondaystat',
            options={'verbose_name': 'GPS поездки'},
        ),
        migrations.AlterModelOptions(
            name='wialontrip',
            options={'verbose_name': 'GPS поездки'},
        ),
        migrations.RenameField(
            model_name='taxitrip',
            old_name='firm_rent',
            new_name='operating_services',
        ),
        migrations.AddField(
            model_name='driver',
            name='fuel_compensation',
            field=models.FloatField(default=50, verbose_name='Процент компенсации топлива'),
        ),
        migrations.AddField(
            model_name='taxitrip',
            name='investor_rent',
            field=models.FloatField(default=0, verbose_name='Прибыль инвестора'),
        ),
        migrations.AlterField(
            model_name='driver',
            name='profit',
            field=models.FloatField(default=50, verbose_name='Процент распределения прибыли'),
        ),
        migrations.AlterField(
            model_name='wialondaystat',
            name='mileage',
            field=models.FloatField(default=0, verbose_name='Пробег по трекеру'),
        ),
        migrations.AlterField(
            model_name='wialontrip',
            name='fuel',
            field=models.PositiveIntegerField(default=0, verbose_name='Раход по трекеру'),
        ),
        migrations.AlterField(
            model_name='wialontrip',
            name='mileage',
            field=models.FloatField(default=0, verbose_name='Пробег по трекеру'),
        ),
        migrations.AlterField(
            model_name='wialontrip',
            name='start',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата начала поездки'),
        ),
        migrations.AlterUniqueTogether(
            name='wialondaystat',
            unique_together={('car', 'stat_date', 'stat_interval')},
        ),
        migrations.AlterUniqueTogether(
            name='wialontrip',
            unique_together={('car', 'start')},
        ),
    ]
