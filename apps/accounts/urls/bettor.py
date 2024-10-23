from django.urls import include, path

from apps.accounts.views import (
    bettor_dashboard,
    bettor_bundles_all,
    bettor_profile,
    bettor_settings,
    bettor_tickets_closed,
    bettor_tickets_all,
    bettor_tickets_detail,
    bettor_tickets_answered,
    bettor_tickets_pending,
    bettor_bundles_purchase,
    bettor_bundles_owned,
    bettor_bundles_detail,
)

app_name = "bettor"

urlpatterns = [
    path("dashboard/", bettor_dashboard, name="dashboard"),
    path(
        "bundles/<uuid:id>/",
        bettor_bundles_detail,
        name="bundles_detail",
    ),
    path(
        "bundles/purchase/<uuid:id>/",
        bettor_bundles_purchase,
        name="bundles_purchase",
    ),
    path("bundles/owned/", bettor_bundles_owned, name="bundles_owned"),
    path("bundles/", bettor_bundles_all, name="bundles_all"),
    path("profile/", bettor_profile, name="profile"),
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
]
