from django.urls import include, path

from .views import (
    admin_groups_all,
    admin_groups_detail,
    admin_groups_running,
    admin_groups_closed,
    admin_groups_new,
    admin_bundles_pending,
    admin_bundles_all,
    admin_bundles_lost,
    admin_bundles_won,
    admin_bundles_detail,
)

app_name = "groups"

urlpatterns = [
    # Groups
    path(
        "groups/",
        include(
            [
                path(
                    "running/",
                    admin_groups_running,
                    name="groups_running",
                ),
                path(
                    "closed/",
                    admin_groups_closed,
                    name="groups_closed",
                ),
                path(
                    "new/",
                    admin_groups_new,
                    name="groups_new",
                ),
                path(
                    "<uuid:group_id>/",
                    admin_groups_detail,
                    name="groups_detail",
                ),
                path(
                    "",
                    admin_groups_all,
                    name="groups_all",
                ),
            ]
        ),
    ),
    # Bundles
    path(
        "bundles/",
        include(
            [
                path(
                    "pending/",
                    admin_bundles_pending,
                    name="bundles_pending",
                ),
                path(
                    "lost/",
                    admin_bundles_lost,
                    name="bundles_lost",
                ),
                path(
                    "won/",
                    admin_bundles_won,
                    name="bundles_won",
                ),
                path(
                    "<uuid:bundle_id>/",
                    admin_bundles_detail,
                    name="bundles_detail",
                ),
                path(
                    "",
                    admin_bundles_all,
                    name="bundles_all",
                ),
            ]
        ),
    ),
]
