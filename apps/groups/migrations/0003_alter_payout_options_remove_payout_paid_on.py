# Generated by Django 5.1.4 on 2024-12-14 02:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("groups", "0002_payout"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="payout",
            options={
                "ordering": ["-created"],
                "verbose_name": "Payout",
                "verbose_name_plural": "Payouts",
            },
        ),
        migrations.RemoveField(
            model_name="payout",
            name="paid_on",
        ),
    ]
