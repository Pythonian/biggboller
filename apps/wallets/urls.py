"""URL configuration for the wallets app."""

from django.urls import path

from .views import (
    wallet_deposit,
    wallet_deposit_confirmation,
    wallet_deposit_pin,
    wallet_deposits,
    wallet_invoice,
    wallet_withdrawal,
    wallet_withdrawal_pin,
    wallet_withdrawals,
)

app_name = "wallet"

urlpatterns = [
    path(
        "deposits/",
        wallet_deposits,
        name="deposits",
    ),
    path(
        "deposit/",
        wallet_deposit,
        name="deposit",
    ),
    path(
        "deposit/confirm/<str:reference>/",
        wallet_deposit_confirmation,
        name="deposit_confirmation",
    ),
    path(
        "deposit/pin/<str:reference>/",
        wallet_deposit_pin,
        name="deposit_pin",
    ),
    path(
        "deposit/invoice/",
        wallet_invoice,
        name="invoice",
    ),
    path(
        "withdrawal/verify/",
        wallet_withdrawal_pin,
        name="withdrawal_pin",
    ),
    path(
        "withdrawals/",
        wallet_withdrawals,
        name="withdrawals",
    ),
    path(
        "withdrawal/",
        wallet_withdrawal,
        name="withdrawal",
    ),
]
