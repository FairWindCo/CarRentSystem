# Generated by Django 3.2.6 on 2022-01-16 19:21

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('carmanagment', '0043_auto_20220116_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brandingamount',
            name='stat_date',
            field=models.DateField(default=datetime.datetime(2022, 1, 16, 19, 21, 11, 538445, tzinfo=utc), verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='carmileage',
            name='stat_date',
            field=models.DateField(default=datetime.datetime(2022, 1, 16, 19, 21, 11, 528479, tzinfo=utc), verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='carsummarystatistics',
            name='branding_amount',
            field=models.FloatField(default=0, verbose_name='Доход за брендирование'),
        ),
        migrations.AlterField(
            model_name='carsummarystatistics',
            name='driver_amount',
            field=models.FloatField(default=0, verbose_name='Зарплата водителя'),
        ),
        migrations.AlterField(
            model_name='carsummarystatistics',
            name='expense',
            field=models.FloatField(default=0, verbose_name='Расходы'),
        ),
        migrations.AlterField(
            model_name='carsummarystatistics',
            name='investor_amount',
            field=models.FloatField(default=0, verbose_name='Прибыль инвестора'),
        ),
        migrations.AlterField(
            model_name='carsummarystatistics',
            name='operate',
            field=models.FloatField(default=0, verbose_name='Операционные затраты'),
        ),
        migrations.AlterField(
            model_name='carsummarystatistics',
            name='rent_amount',
            field=models.FloatField(default=0, verbose_name='Доход от аренды'),
        ),
        migrations.AlterField(
            model_name='carsummarystatistics',
            name='stat_date',
            field=models.DateField(default=datetime.datetime(2022, 1, 16, 19, 21, 11, 528479, tzinfo=utc), verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='carsummarystatistics',
            name='taxi_amount',
            field=models.FloatField(default=0, verbose_name='Доход от таксопарка'),
        ),
        migrations.AlterField(
            model_name='tripstatistics',
            name='stat_date',
            field=models.DateField(default=datetime.datetime(2022, 1, 16, 19, 21, 11, 538445, tzinfo=utc), verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='wialondaystat',
            name='stat_date',
            field=models.DateField(default=datetime.datetime(2022, 1, 16, 19, 21, 11, 539442, tzinfo=utc), verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='wialontrip',
            name='start',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 16, 19, 21, 11, 539442, tzinfo=utc), verbose_name='Дата начала поездки'),
        ),
        migrations.AlterUniqueTogether(
            name='carsummarystatistics',
            unique_together={('car', 'stat_date')},
        ),
    ]
