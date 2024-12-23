# Generated by Django 5.1.4 on 2024-12-23 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0003_alter_payout_options_remove_payout_paid_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='bundle',
            name='current_round',
            field=models.PositiveIntegerField(default=1, help_text='The current round of the bundle (1-4).', verbose_name='Current Round'),
        ),
        migrations.AddField(
            model_name='bundle',
            name='round_outcomes',
            field=models.JSONField(default=dict, help_text="A dictionary storing the outcomes of each round, e.g., {1: 'L', 2: 'W'}.", verbose_name='Round Outcomes'),
        ),
    ]
