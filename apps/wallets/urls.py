from django.urls import path
from .views import (
    wallet_deposit,
    wallet_invoice,
    wallet_deposit_confirmation,
    wallet_withdrawal,
)

app_name = "wallet"

urlpatterns = [
    path("deposit/", wallet_deposit, name="deposit"),
    path(
        "deposit/confirm/<str:reference>/",
        wallet_deposit_confirmation,
        name="confirmation",
    ),
    path("deposit/invoice/", wallet_invoice, name="invoice"),
    path("withdrawal/", wallet_withdrawal, name="withdrawal"),
]
