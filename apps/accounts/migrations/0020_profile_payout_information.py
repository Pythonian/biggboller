# Generated by Django 5.1.1 on 2024-10-28 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_deposit_payout_amount_payout'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='payout_information',
            field=models.TextField(blank=True, help_text='Bank account information for Payouts', verbose_name='Payout Information'),
        ),
    ]
