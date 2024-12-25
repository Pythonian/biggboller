from django.urls import include, path

from .views import (
    admin_tickets_closed,
    admin_tickets_all,
    admin_tickets_detail,
    admin_tickets_answered,
    admin_tickets_pending,
    bettor_tickets_closed,
    bettor_tickets_all,
    bettor_tickets_detail,
    bettor_tickets_answered,
    bettor_tickets_pending,
)

app_name = "ticket"

urlpatterns = [
    # Administrator Tickets
    path(
        "administrator/tickets/",
        include(
            [
                path(
                    "closed/",
                    admin_tickets_closed,
                    name="admin_tickets_closed",
                ),
                path(
                    "answered/",
                    admin_tickets_answered,
                    name="admin_tickets_answered",
                ),
                path(
                    "pending/",
                    admin_tickets_pending,
                    name="admin_tickets_pending",
                ),
                path(
                    "<str:ticket_id>/",
                    admin_tickets_detail,
                    name="admin_tickets_detail",
                ),
                path(
                    "",
                    admin_tickets_all,
                    name="admin_tickets_all",
                ),
            ]
        ),
    ),
    # Bettor Tickets
    path(
        "bettor/tickets/",
        include(
            [
                path(
                    "closed/",
                    bettor_tickets_closed,
                    name="bettor_tickets_closed",
                ),
                path(
                    "answered/",
                    bettor_tickets_answered,
                    name="bettor_tickets_answered",
                ),
                path(
                    "pending/",
                    bettor_tickets_pending,
                    name="bettor_tickets_pending",
                ),
                path(
                    "<str:ticket_id>/",
                    bettor_tickets_detail,
                    name="bettor_tickets_detail",
                ),
                path(
                    "",
                    bettor_tickets_all,
                    name="bettor_tickets_all",
                ),
            ]
        ),
    ),
]
