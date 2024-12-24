from django.urls import include, path

from apps.accounts.views import (
    onboarding_form,
    update_transaction_pin,
    bettor_dashboard,
    bettor_settings,
    bettor_tickets_closed,
    bettor_tickets_all,
    bettor_tickets_detail,
    bettor_tickets_answered,
    bettor_tickets_pending,
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
    # Tickets
    path(
        "tickets/",
        include(
            [
                path(
                    "closed/",
                    bettor_tickets_closed,
                    name="tickets_closed",
                ),
                path(
                    "answered/",
                    bettor_tickets_answered,
                    name="tickets_answered",
                ),
                path(
                    "pending/",
                    bettor_tickets_pending,
                    name="tickets_pending",
                ),
                path(
                    "<str:ticket_id>/",
                    bettor_tickets_detail,
                    name="tickets_detail",
                ),
                path(
                    "",
                    bettor_tickets_all,
                    name="tickets_all",
                ),
            ]
        ),
    ),
    # Payouts
    path(
        "payouts/",
        include(
            [
                path(
                    "",
                    bettor_payouts_all,
                    name="payouts_all",
                ),
            ]
        ),
    ),
]
