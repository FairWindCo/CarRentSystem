# Generated by Django 3.2.6 on 2021-09-07 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carmanagment', '0006_auto_20210903_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='profit',
            field=models.FloatField(default=0.5, verbose_name='Коифициент распределения прибыли'),
        ),
        migrations.AddField(
            model_name='taxitrip',
            name='car_amount',
            field=models.PositiveBigIntegerField(default=0, verbose_name='Сумма прибыли по машине'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='car',
            name='control_mileage',
            field=models.PositiveIntegerField(verbose_name='Контрольное значени пробега'),
        ),
        migrations.AlterField(
            model_name='car',
            name='last_TO_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='investor',
            name='profit',
            field=models.FloatField(verbose_name='Коифициент распределения прибыли'),
        ),
        migrations.AlterField(
            model_name='taxitrip',
            name='fuel',
            field=models.PositiveIntegerField(verbose_name='Затраты на топливо'),
        ),
    ]
