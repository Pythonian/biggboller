# Generated by Django 5.1.1 on 2024-12-01 08:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0032_alter_profile_payout_information'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bundle',
            name='maximum_win_multiplier',
        ),
        migrations.RemoveField(
            model_name='bundle',
            name='minimum_win_multiplier',
        ),
        migrations.AddField(
            model_name='bundle',
            name='winning_percentage',
            field=models.DecimalField(decimal_places=2, default=1, help_text='Enter the percentage of the bundle price that will be returned as winnings. E.g., 20 for 20%.', max_digits=5, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='Winning Percentage'),
            preserve_default=False,
        ),
    ]
