# Generated by Django 3.2.6 on 2021-09-08 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carmanagment', '0007_auto_20210907_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='carmodel',
            name='type_class',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Бензин А95'), (2, 'Бензин А95'), (3, 'Дизельное топливо'), (4, 'Сжиженный газ')], default=4, verbose_name='Тип топлива'),
        ),
    ]
