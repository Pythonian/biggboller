from apps.accounts.views.administrator import (
    admin_bundles_all,
    admin_bundles_lost,
    admin_bundles_pending,
    admin_bundles_won,
    admin_bundles_detail,
    admin_dashboard,
    admin_groups_all,
    admin_groups_detail,
    admin_groups_closed,
    admin_groups_new,
    admin_groups_running,
    admin_users_active,
    admin_users_all,
    admin_users_banned,
    admin_users_deactivated,
    admin_users_notifications,
    admin_users_verified,
    admin_users_unverified,
    admin_tickets_closed,
    admin_tickets_all,
    admin_tickets_answered,
    admin_tickets_pending,
    admin_deposits_rejected,
    admin_deposits_all,
    admin_deposits_approved,
    admin_deposits_pending,
    admin_withdrawals_rejected,
    admin_withdrawals_all,
    admin_withdrawals_approved,
    admin_withdrawals_pending,
)
from apps.accounts.views.bettor import bettor_dashboard

__all__ = [
    "admin_dashboard",
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
    "admin_users_active",
    "admin_users_all",
    "admin_users_banned",
    "admin_users_deactivated",
    "admin_users_notifications",
    "admin_users_verified",
    "admin_users_unverified",
    "admin_tickets_closed",
    "admin_tickets_all",
    "admin_tickets_answered",
    "admin_tickets_pending",
    "admin_deposits_rejected",
    "admin_deposits_all",
    "admin_deposits_approved",
    "admin_deposits_pending",
    "admin_withdrawals_rejected",
    "admin_withdrawals_all",
    "admin_withdrawals_approved",
    "admin_withdrawals_pending",
    # Bettor
    "bettor_dashboard",
]
