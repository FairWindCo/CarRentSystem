# Generated by Django 3.2.6 on 2021-09-20 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('balance', '0003_alter_transaction_transactiontype'),
    ]

    operations = [
        migrations.AddField(
            model_name='accounttransaction',
            name='comment',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='comment',
            field=models.TextField(blank=True, default='', max_length=1000, null=True),
        ),
    ]
