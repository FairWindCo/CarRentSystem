# Generated by Django 3.2.6 on 2021-12-05 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carmanagment', '0023_taxioperator_cash_box'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='carschedule',
            options={'verbose_name': 'Аренда авто', 'verbose_name_plural': 'Расписание аренды авто'},
        ),
        migrations.RemoveField(
            model_name='carschedule',
            name='rent_price',
        ),
        migrations.AddField(
            model_name='carschedule',
            name='deposit',
            field=models.PositiveIntegerField(default=0.0, verbose_name='Залог'),
        ),
        migrations.AddField(
            model_name='carschedule',
            name='rent_amount',
            field=models.PositiveIntegerField(default=0.0, verbose_name='Сумма оренды'),
        ),
        migrations.DeleteModel(
            name='CarDayRent',
        ),
    ]
