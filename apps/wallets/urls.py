from django.urls import path
from .views import (
    wallet_deposit,
    wallet_deposit_pin,
    wallet_invoice,
    wallet_deposit_confirmation,
    wallet_withdrawal,
    wallet_withdrawal_pin,
)

app_name = "wallet"

urlpatterns = [
    path("deposit/", wallet_deposit, name="deposit"),
    path(
        "deposit/confirm/<str:reference>/",
        wallet_deposit_confirmation,
        name="deposit_confirmation",
    ),
    path("deposit/pin/<str:reference>/", wallet_deposit_pin, name="deposit_pin"),
    path("deposit/invoice/", wallet_invoice, name="invoice"),
    path("withdrawal/verify/", wallet_withdrawal_pin, name="withdrawal_pin"),
    path("withdrawal/", wallet_withdrawal, name="withdrawal"),
]
