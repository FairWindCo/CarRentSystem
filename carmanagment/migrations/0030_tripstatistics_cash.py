# Generated by Django 3.2.6 on 2021-12-12 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carmanagment', '0029_auto_20211212_1046'),
    ]

    operations = [
        migrations.AddField(
            model_name='tripstatistics',
            name='cash',
            field=models.FloatField(default=0, verbose_name='Сумма наличнных'),
        ),
    ]
