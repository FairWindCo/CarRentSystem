# Generated by Django 3.2.6 on 2021-10-17 12:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('carmanagment', '0016_auto_20211008_1103'),
    ]

    operations = [
        migrations.CreateModel(
            name='TripStatistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stat_date', models.DateField(auto_created=True, verbose_name='Дата')),
                ('mileage', models.FloatField(verbose_name='Пробег по трекеру')),
                ('fuel', models.FloatField(verbose_name='Затраты на топливо')),
                ('amount', models.FloatField(verbose_name='Сумма оплаты')),
                ('car_amount', models.FloatField(verbose_name='Сумма прибыли по машине')),
                ('payer_amount', models.FloatField(default=0, verbose_name='Прибыль сервиса')),
                ('driver_amount', models.FloatField(default=0, verbose_name='Зарплата водителя')),
                ('expanse_amount', models.FloatField(default=0, verbose_name='Затраты по машине')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carmanagment.car')),
            ],
            options={
                'unique_together': {('car', 'stat_date')},
            },
        ),
    ]
