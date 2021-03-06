# Generated by Django 3.2.6 on 2021-12-05 18:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('carmanagment', '0025_auto_20211205_1243'),
    ]

    operations = [
        migrations.AddField(
            model_name='carschedule',
            name='driver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='carmanagment.driver', verbose_name='Арендатор'),
        ),
        migrations.AddField(
            model_name='taxioperator',
            name='bank_interest',
            field=models.FloatField(default=0.025, verbose_name='Комисия за перевод (без нал)'),
        ),
        migrations.AddField(
            model_name='taxitrip',
            name='bank_amount',
            field=models.FloatField(default=0, verbose_name='Комисия банка'),
        ),
        migrations.AddField(
            model_name='taxitrip',
            name='firm_rent',
            field=models.FloatField(default=0, verbose_name='Операционные услуги'),
        ),
        migrations.AddField(
            model_name='taxitrip',
            name='total_payer_amount',
            field=models.FloatField(default=0, verbose_name='Деньги сервиса'),
        ),
        migrations.AddField(
            model_name='tripstatistics',
            name='total_bank_rent',
            field=models.FloatField(default=0, verbose_name='Банк процент'),
        ),
        migrations.AddField(
            model_name='tripstatistics',
            name='total_firm_rent',
            field=models.FloatField(default=0, verbose_name='Операционные затрты'),
        ),
        migrations.AddField(
            model_name='tripstatistics',
            name='total_payer_amount',
            field=models.FloatField(default=0, verbose_name='Деньги для сервиса'),
        ),
        migrations.AlterField(
            model_name='taxioperator',
            name='profit',
            field=models.FloatField(default=0.15, verbose_name='Коифициент прибили с поезди оператора (без нал)'),
        ),
    ]
