from django.urls import path

from apps.accounts.views import (
    onboarding_form,
    update_transaction_pin,
    bettor_dashboard,
    bettor_settings,
    bettor_payouts_all,
)

app_name = "bettor"

urlpatterns = [
    path(
        "onboarding/",
        onboarding_form,
        name="onboarding_form",
    ),
    path(
        "settings/update-pin/",
        update_transaction_pin,
        name="update_transaction_pin",
    ),
    path("dashboard/", bettor_dashboard, name="dashboard"),
    path("settings/", bettor_settings, name="settings"),
    path("payouts/", bettor_payouts_all, name="payouts_all"),
]
