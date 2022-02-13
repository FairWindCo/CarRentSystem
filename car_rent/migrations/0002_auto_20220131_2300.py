# Generated by Django 3.2.6 on 2022-01-31 21:00

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('car_management', '0002_auto_20220131_2300'),
        ('car_rent', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='carsinoperator',
            options={'ordering': ('car__name', 'signal', 'operator'), 'verbose_name': 'Машины в таксопарках', 'verbose_name_plural': 'Машины в таксопарках'},
        ),
        migrations.AddField(
            model_name='carschedule',
            name='price',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='scheduled_terms', to='car_management.rentprice', verbose_name='тариф аренды'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='brandingamount',
            name='stat_date',
            field=models.DateField(default=datetime.datetime(2022, 1, 31, 21, 0, 25, 397914, tzinfo=utc), verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='carschedule',
            name='term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scheduled_terms', to='car_management.rentterms', verbose_name='условия аренды'),
        ),
    ]