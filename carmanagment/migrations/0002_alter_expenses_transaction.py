# Generated by Django 3.2.6 on 2021-08-27 09:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('balance', '0001_initial'),
        ('carmanagment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenses',
            name='transaction',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='expense', to='balance.transaction'),
        ),
    ]
