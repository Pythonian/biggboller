from apps.accounts.views.administrator import (
    admin_dashboard,
    admin_users_login_history,
    admin_wallet_deposit_history,
    admin_users_active,
    admin_users_all,
    admin_users_banned,
    admin_users_deactivated,
    admin_users_verified,
    admin_users_unverified,
    admin_users_detail,
    admin_users_assign_group,
    admin_unban_user,
    admin_suspend_user,
    admin_tickets_closed,
    admin_tickets_all,
    admin_tickets_detail,
    admin_tickets_answered,
    admin_tickets_pending,
    admin_payouts_all,
    admin_payouts_approved,
    admin_payouts_cancelled,
    admin_withdrawals_all,
    admin_withdrawals_approved,
    admin_withdrawals_pending,
    admin_withdrawals_cancelled,
    admin_process_withdrawal,
)
from apps.accounts.views.bettor import (
    onboarding_form,
    update_transaction_pin,
    bettor_dashboard,
    bettor_bundles_all,
    bettor_settings,
    bettor_tickets_closed,
    bettor_tickets_all,
    bettor_tickets_detail,
    bettor_tickets_answered,
    bettor_tickets_pending,
    bettor_purchase_successful,
    bettor_bundles_owned,
    bettor_bundles_detail,
    bettor_bundle_purchase_pin,
    bettor_payouts_all,
)

__all__ = [
    "admin_dashboard",
    "admin_users_login_history",
    "admin_wallet_deposit_history",
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
    "admin_users_detail",
    "admin_unban_user",
    "admin_suspend_user",
    "admin_users_banned",
    "admin_users_deactivated",
    "admin_users_verified",
    "admin_users_unverified",
    "admin_users_assign_group",
    "admin_tickets_closed",
    "admin_tickets_all",
    "admin_tickets_detail",
    "admin_tickets_answered",
    "admin_tickets_pending",
    "admin_payouts_all",
    "admin_payouts_approved",
    "admin_payouts_cancelled",
    "admin_withdrawals_all",
    "admin_withdrawals_approved",
    "admin_withdrawals_pending",
    "admin_withdrawals_cancelled",
    "admin_process_withdrawal",
    # Bettor
    "onboarding_form",
    "update_transaction_pin",
    "bettor_dashboard",
    "bettor_bundles_all",
    "bettor_settings",
    "bettor_tickets_closed",
    "bettor_tickets_all",
    "bettor_tickets_detail",
    "bettor_tickets_answered",
    "bettor_tickets_pending",
    "bettor_bundles_owned",
    "bettor_bundles_detail",
    "bettor_bundle_purchase_pin",
    "bettor_purchase_successful",
    "bettor_payouts_all",
]
