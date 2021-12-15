# Generated by Django 3.2.6 on 2021-12-15 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carmanagment', '0030_tripstatistics_cash'),
    ]

    operations = [
        migrations.AddField(
            model_name='tripstatistics',
            name='car_in_rent',
            field=models.BooleanField(default=False, verbose_name='Машина в аренде'),
        ),
        migrations.AlterUniqueTogether(
            name='tripstatistics',
            unique_together={('car', 'stat_date', 'car_in_rent')},
        ),
        migrations.AlterIndexTogether(
            name='tripstatistics',
            index_together={('car', 'stat_date')},
        ),
        migrations.RemoveField(
            model_name='tripstatistics',
            name='lost_amount',
        ),
        migrations.RemoveField(
            model_name='tripstatistics',
            name='rent_amount',
        ),
        migrations.RemoveField(
            model_name='tripstatistics',
            name='rent_mileage',
        ),
    ]
