# Generated by Django 5.1.4 on 2024-12-24 19:23

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wallets", "0003_alter_deposit_description"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(
                fields=["wallet"], name="wallets_aud_wallet__ca9400_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(
                fields=["transaction_type"], name="wallets_aud_transac_f623b6_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="deposit",
            index=models.Index(fields=["user"], name="wallets_dep_user_id_6290bd_idx"),
        ),
        migrations.AddIndex(
            model_name="deposit",
            index=models.Index(
                fields=["reference"], name="wallets_dep_referen_ccb9cd_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="deposit",
            index=models.Index(fields=["status"], name="wallets_dep_status_cf9277_idx"),
        ),
        migrations.AddIndex(
            model_name="wallet",
            index=models.Index(fields=["user"], name="wallets_wal_user_id_006796_idx"),
        ),
        migrations.AddIndex(
            model_name="withdrawal",
            index=models.Index(fields=["user"], name="wallets_wit_user_id_67d677_idx"),
        ),
        migrations.AddIndex(
            model_name="withdrawal",
            index=models.Index(
                fields=["reference"], name="wallets_wit_referen_2e4486_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="withdrawal",
            index=models.Index(fields=["status"], name="wallets_wit_status_ddea9b_idx"),
        ),
    ]
