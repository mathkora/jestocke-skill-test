# Generated by Django 4.2.5 on 2023-11-09 00:45

from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('market_place', '0007_storagebox_monthly_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storagebox',
            name='monthly_price',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default_currency='EUR', max_digits=14),
        ),
    ]
