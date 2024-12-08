from django.urls import include, path

from apps.accounts.views import (
    bettor_dashboard,
    bettor_bundles_all,
    bettor_settings,
    bettor_tickets_closed,
    bettor_tickets_all,
    bettor_tickets_detail,
    bettor_tickets_answered,
    bettor_tickets_pending,
    # bettor_bundles_purchase,
    bettor_bundles_owned,
    bettor_bundles_detail,
    bettor_purchase_successful,
    bettor_deposits_all,
    bettor_deposits_approved,
    bettor_deposits_pending,
    bettor_deposits_cancelled,
    bettor_payouts_all,
    bettor_payouts_approved,
    bettor_payouts_pending,
    bettor_payouts_cancelled,
)

app_name = "bettor"

urlpatterns = [
    path("dashboard/", bettor_dashboard, name="dashboard"),
    path(
        "bundles/purchase/<uuid:bundle_id>/",
        bettor_bundles_detail,
        name="bundles_detail",
    ),
    # path(
    #     "bundles/pur/<uuid:bundle_id>/",
    #     bettor_bundles_purchase,
    #     name="bundles_purchase",
    # ),
    path(
        "bundles/purchase/<uuid:purchase_id>/successful/",
        bettor_purchase_successful,
        name="purchase_successful",
    ),
    path("bundles/owned/", bettor_bundles_owned, name="bundles_owned"),
    path("bundles/", bettor_bundles_all, name="bundles_all"),
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
    # Deposits
    path(
        "deposits/",
        include(
            [
                path(
                    "approved/",
                    bettor_deposits_approved,
                    name="deposits_approved",
                ),
                path(
                    "pending/",
                    bettor_deposits_pending,
                    name="deposits_pending",
                ),
                path(
                    "cancelled/",
                    bettor_deposits_cancelled,
                    name="deposits_cancelled",
                ),
                path(
                    "",
                    bettor_deposits_all,
                    name="deposits_all",
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
                    "approved/",
                    bettor_payouts_approved,
                    name="payouts_approved",
                ),
                path(
                    "pending/",
                    bettor_payouts_pending,
                    name="payouts_pending",
                ),
                path(
                    "cancelled/",
                    bettor_payouts_cancelled,
                    name="payouts_cancelled",
                ),
                path(
                    "",
                    bettor_payouts_all,
                    name="payouts_all",
                ),
            ]
        ),
    ),
]
