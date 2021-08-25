# Generated by Django 3.2.6 on 2021-08-25 10:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='TransactionType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transactionTime', models.DateTimeField(auto_created=True, auto_now_add=True)),
                ('transactionType', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='balance.transactiontype')),
            ],
        ),
        migrations.CreateModel(
            name='AccountTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.BigIntegerField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='balance.account')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='balance.transaction')),
            ],
        ),
        migrations.CreateModel(
            name='AccountStatement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statementDate', models.DateField(auto_created=True, auto_now_add=True)),
                ('closingBalance', models.BigIntegerField()),
                ('totalCredit', models.BigIntegerField()),
                ('totalDebit', models.BigIntegerField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='balance.account')),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='last_period_balance',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='for_account', to='balance.accountstatement'),
        ),
    ]
