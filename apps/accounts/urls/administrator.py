from django.urls import include, path

from apps.accounts.views import (
    admin_dashboard,
    admin_users_login_history,
    admin_users_active,
    admin_users_all,
    admin_users_banned,
    admin_users_deactivated,
    admin_users_notifications,
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
    # admin_deposits_cancelled,
    # admin_deposits_all,
    # admin_deposits_approved,
    # admin_deposits_update_payout,
    # admin_deposits_pending,
    admin_payouts_all,
    admin_payouts_approved,
    admin_payouts_pending,
    admin_payouts_cancelled,
    admin_withdrawals_all,
    admin_withdrawals_approved,
    admin_withdrawals_pending,
    admin_withdrawals_cancelled,
    admin_process_withdrawal,
)

app_name = "administrator"

urlpatterns = [
    path(
        "login-history/",
        admin_users_login_history,
        name="login_history",
    ),
    path("dashboard/", admin_dashboard, name="dashboard"),
    # Deposits
    # path(
    #     "deposits/",
    #     include(
    #         [
    #             path(
    #                 "cancelled/",
    #                 admin_deposits_cancelled,
    #                 name="deposits_cancelled",
    #             ),
    #             path(
    #                 "approved/",
    #                 admin_deposits_approved,
    #                 name="deposits_approved",
    #             ),
    #             path(
    #                 "pending/",
    #                 admin_deposits_pending,
    #                 name="deposits_pending",
    #             ),
    #             path(
    #                 "update-payout/<uuid:deposit_id>/",
    #                 admin_deposits_update_payout,
    #                 name="deposits_update_payout",
    #             ),
    #             path(
    #                 "",
    #                 admin_deposits_all,
    #                 name="deposits_all",
    #             ),
    #         ]
    #     ),
    # ),
    # Withdrawals
    path(
        "withdrawals/",
        include(
            [
                path(
                    "approved/",
                    admin_withdrawals_approved,
                    name="withdrawals_approved",
                ),
                path(
                    "pending/",
                    admin_withdrawals_pending,
                    name="withdrawals_pending",
                ),
                path(
                    "cancelled/",
                    admin_withdrawals_cancelled,
                    name="withdrawals_cancelled",
                ),
                path(
                    "process/<uuid:withdrawal_id>/",
                    admin_process_withdrawal,
                    name="process_withdrawal",
                ),
                path(
                    "",
                    admin_withdrawals_all,
                    name="withdrawals_all",
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
                    admin_payouts_approved,
                    name="payouts_approved",
                ),
                path(
                    "pending/",
                    admin_payouts_pending,
                    name="payouts_pending",
                ),
                path(
                    "cancelled/",
                    admin_payouts_cancelled,
                    name="payouts_cancelled",
                ),
                path(
                    "",
                    admin_payouts_all,
                    name="payouts_all",
                ),
            ]
        ),
    ),
    # Tickets
    path(
        "tickets/",
        include(
            [
                path(
                    "closed/",
                    admin_tickets_closed,
                    name="tickets_closed",
                ),
                path(
                    "answered/",
                    admin_tickets_answered,
                    name="tickets_answered",
                ),
                path(
                    "pending/",
                    admin_tickets_pending,
                    name="tickets_pending",
                ),
                path(
                    "<str:ticket_id>/",
                    admin_tickets_detail,
                    name="tickets_detail",
                ),
                path(
                    "",
                    admin_tickets_all,
                    name="tickets_all",
                ),
            ]
        ),
    ),
    # Users
    path(
        "users/",
        include(
            [
                path(
                    "active/",
                    admin_users_active,
                    name="users_active",
                ),
                path(
                    "banned/",
                    admin_users_banned,
                    name="users_banned",
                ),
                path(
                    "unverified/",
                    admin_users_unverified,
                    name="users_unverified",
                ),
                path(
                    "verified/",
                    admin_users_verified,
                    name="users_verified",
                ),
                path(
                    "notifications/",
                    admin_users_notifications,
                    name="users_notifications",
                ),
                path(
                    "deactivated/",
                    admin_users_deactivated,
                    name="users_deactivated",
                ),
                path(
                    "<str:username>/suspend/",
                    admin_suspend_user,
                    name="suspend_user",
                ),
                path(
                    "<str:username>/unban/",
                    admin_unban_user,
                    name="unban_user",
                ),
                path(
                    "<str:username>/assigngroup/",
                    admin_users_assign_group,
                    name="assign_group",
                ),
                path(
                    "<str:username>/",
                    admin_users_detail,
                    name="users_detail",
                ),
                path(
                    "",
                    admin_users_all,
                    name="users_all",
                ),
            ]
        ),
    ),
    # # Groups
    # path(
    #     "groups/",
    #     include(
    #         [
    #             path(
    #                 "running/",
    #                 admin_groups_running,
    #                 name="groups_running",
    #             ),
    #             path(
    #                 "closed/",
    #                 admin_groups_closed,
    #                 name="groups_closed",
    #             ),
    #             path(
    #                 "new/",
    #                 admin_groups_new,
    #                 name="groups_new",
    #             ),
    #             path(
    #                 "<uuid:group_id>/",
    #                 admin_groups_detail,
    #                 name="groups_detail",
    #             ),
    #             path(
    #                 "",
    #                 admin_groups_all,
    #                 name="groups_all",
    #             ),
    #         ]
    #     ),
    # ),
    # # Bundles
    # path(
    #     "bundles/",
    #     include(
    #         [
    #             path(
    #                 "pending/",
    #                 admin_bundles_pending,
    #                 name="bundles_pending",
    #             ),
    #             path(
    #                 "lost/",
    #                 admin_bundles_lost,
    #                 name="bundles_lost",
    #             ),
    #             path(
    #                 "won/",
    #                 admin_bundles_won,
    #                 name="bundles_won",
    #             ),
    #             path(
    #                 "<uuid:bundle_id>/",
    #                 admin_bundles_detail,
    #                 name="bundles_detail",
    #             ),
    #             path(
    #                 "",
    #                 admin_bundles_all,
    #                 name="bundles_all",
    #             ),
    #         ]
    #     ),
    # ),
]
