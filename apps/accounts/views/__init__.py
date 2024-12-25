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
    bettor_settings,
    bettor_payouts_all,
)

__all__ = [
    "admin_dashboard",
    "admin_users_login_history",
    "admin_wallet_deposit_history",
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
    "bettor_settings",
    "bettor_payouts_all",
]
