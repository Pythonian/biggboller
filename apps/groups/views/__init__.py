from apps.groups.views.administrator import (
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
    approve_group_request,
    reject_group_request,
)

from apps.groups.views.bettor import (
    bettor_groups_all,
    bettor_groups_available,
    bettor_bundle_detail,
    bettor_bundles_owned,
)

__all__ = [
    # Administrator
    "admin_groups_all",
    "admin_groups_detail",
    "admin_groups_running",
    "admin_groups_closed",
    "admin_groups_new",
    "admin_bundles_pending",
    "admin_bundles_all",
    "admin_bundles_lost",
    "admin_bundles_won",
    "admin_bundles_detail",
    "approve_group_request",
    "reject_group_request",
    # Bettor
    "bettor_groups_all",
    "bettor_groups_available",
    "bettor_bundle_detail",
    "bettor_bundles_owned",
]
