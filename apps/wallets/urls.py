from django.urls import path
from .views import wallet_deposit, wallet_invoice, wallet_deposit_confirmation

app_name = "wallet"

urlpatterns = [
    path("deposit/", wallet_deposit, name="deposit"),
    path("deposit/confirm/", wallet_deposit_confirmation, name="confirmation"),
    path("deposit/invoice/", wallet_invoice, name="invoice"),
]
