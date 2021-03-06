# Generated by Django 3.2.6 on 2021-09-15 09:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('carmanagment', '0008_carmodel_type_class'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyList_model',
            fields=[
                ('car_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='carmanagment.car')),
            ],
            bases=('carmanagment.car',),
        ),
        migrations.CreateModel(
            name='TaxiOperator',
            fields=[
                ('counterpart_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='carmanagment.counterpart')),
                ('cash_profit', models.FloatField(default=0.15, verbose_name='Коифициент прибили с поезди оператора (нал)')),
                ('profit', models.FloatField(default=0.17, verbose_name='Коифициент прибили с поезди оператора (без нал)')),
            ],
            options={
                'verbose_name': 'Оператор такси',
                'verbose_name_plural': 'Оператор такси',
            },
            bases=('carmanagment.counterpart',),
        ),
        migrations.CreateModel(
            name='CarsInOperator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('car_uid', models.CharField(blank=True, max_length=255, null=True, verbose_name='Идентификатор машины')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cars_in_taxi', to='carmanagment.car', verbose_name='Машина')),
                ('operator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taxi_park', to='carmanagment.taxioperator', verbose_name='Таксопарк')),
            ],
            options={
                'verbose_name': 'Оператор такси',
                'verbose_name_plural': 'Оператор такси',
            },
        ),
    ]
