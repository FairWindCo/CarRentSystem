# Generated by Django 3.2.6 on 2022-02-05 22:17

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('trip_stat', '0003_alter_carsummarystatistics_stat_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carsummarystatistics',
            name='stat_date',
            field=models.DateField(default=datetime.datetime(2022, 2, 5, 22, 17, 46, 691976, tzinfo=utc), verbose_name='Дата'),
        ),
    ]