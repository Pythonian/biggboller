from decimal import Decimal
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.html import strip_tags
from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.utils.timezone import now

from apps.accounts.models import (
    Ticket,
    Profile,
    Action,
    # Deposit,
    # Payout,
    LoginHistory,
)
from apps.accounts.forms import TicketReplyForm
from apps.accounts.utils import create_action, send_email_thread
from apps.core.utils import mk_paginator
from apps.wallets.models import Withdrawal
from apps.groups.models import Group, Bundle, Purchase, Payout

logger = logging.getLogger(__name__)

PAGINATION_COUNT = 20


def is_admin(user):
    """
    Check if the user has admin privileges.
    Adjust this function based on your authentication setup.
    """
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    groups = Group.objects.all()
    total_groups = groups.count()
    running_groups = groups.filter(status=Group.Status.RUNNING).count()

    bundles = Bundle.objects.all()
    total_bundles = bundles.count()
    pending_bundles = bundles.filter(status=Bundle.Status.PENDING).count()

    tickets = Ticket.objects.all()
    total_tickets = tickets.count()
    pending_tickets = tickets.filter(status=Ticket.Status.PENDING).count()

    bettors = Profile.objects.filter(user__is_staff=False)
    total_users = bettors.count()
    active_users = bettors.filter(email_confirmed=True).count()

    activities = Action.objects.exclude(user=request.user)[:5]

    # Get the top 5 bundles based on staked amount
    top_bundles = (
        Purchase.objects.filter(status=Purchase.Status.APPROVED)
        .values("bundle__name", "bundle__group__name")
        .annotate(total_amount=models.Sum("amount"))
        .order_by("-total_amount")[:5]
    )

    # Get the latest 5 bundle purchases
    latest_purchases = (
        Purchase.objects.filter(status=Purchase.Status.APPROVED)
        .select_related("user__profile")
        .values("user__last_name", "user__first_name", "amount")
        .order_by("-created")[:5]
    )

    # Get the latest 5 payouts
    # latest_payouts = (
    #     Payout.objects.filter(status=Payout.Status.APPROVED)
    #     .select_related("user__profile")
    #     .values("user__last_name", "user__first_name", "amount", "paid_on")
    #     .order_by("-paid_on")[:5]
    # )

    # Calculate the total stakes
    total_purchases = Purchase.objects.filter(
        status=Purchase.Status.APPROVED
    ).aggregate(total=models.Sum("amount")).get("total") or Decimal("0.00")

    # Calculate the total payouts
    total_payouts = Payout.objects.filter(status=Payout.Status.APPROVED).aggregate(
        total=models.Sum("amount")
    ).get("total") or Decimal("0.00")

    template = "accounts/administrator/dashboard.html"
    context = {
        "total_groups": total_groups,
        "running_groups": running_groups,
        "total_bundles": total_bundles,
        "pending_bundles": pending_bundles,
        "total_tickets": total_tickets,
        "pending_tickets": pending_tickets,
        "total_users": total_users,
        "active_users": active_users,
        "activities": activities,
        "top_bundles": top_bundles,
        "latest_purchases": latest_purchases,
        "total_purchases": total_purchases,
        # "latest_payouts": latest_payouts,
        "total_payouts": total_payouts,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_users_login_history(request):
    if request.user.is_staff:
        login_records = LoginHistory.objects.select_related("user")
    else:
        login_records = LoginHistory.objects.select_related("user").filter(
            user__is_staff=False
        )

    login_records = mk_paginator(request, login_records, PAGINATION_COUNT)

    template = "accounts/administrator/login_history.html"
    context = {
        "login_records": login_records,
    }

    return render(request, template, context)


##############
# USERS
##############


@login_required
@user_passes_test(is_admin)
def admin_users_all(request):
    bettors = Profile.objects.filter(user__is_staff=False)
    registered_users = bettors.count()
    active_users = bettors.filter(
        email_confirmed=True,
        is_banned=False,
        user__is_active=True,
    ).count()
    banned_users = bettors.filter(is_banned=True).count()
    deactivated_users = bettors.filter(user__is_active=False).count()

    bettors = mk_paginator(request, bettors, PAGINATION_COUNT)

    template = "accounts/administrator/users/all.html"
    context = {
        "bettors": bettors,
        "registered_users": registered_users,
        "deactivated_users": deactivated_users,
        "active_users": active_users,
        "banned_users": banned_users,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_users_active(request):
    bettors = Profile.objects.filter(
        user__is_staff=False,
        email_confirmed=True,
        is_banned=False,
    )
    active_users = bettors.count()

    bettors = mk_paginator(request, bettors, PAGINATION_COUNT)

    template = "accounts/administrator/users/active.html"
    context = {
        "bettors": bettors,
        "active_users": active_users,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_users_banned(request):
    bettors = Profile.objects.filter(
        user__is_staff=False,
        is_banned=True,
    )
    banned_users = bettors.count()

    bettors = mk_paginator(request, bettors, PAGINATION_COUNT)

    template = "accounts/administrator/users/banned.html"
    context = {
        "bettors": bettors,
        "banned_users": banned_users,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_users_unverified(request):
    bettors = Profile.objects.filter(
        user__is_staff=False,
        verified_account=False,
    )
    unverified_users = bettors.count()

    bettors = mk_paginator(request, bettors, PAGINATION_COUNT)

    template = "accounts/administrator/users/unverified.html"
    context = {
        "bettors": bettors,
        "unverified_users": unverified_users,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_users_verified(request):
    bettors = Profile.objects.filter(
        user__is_staff=False,
        verified_account=True,
    )
    verified_users = bettors.count()

    bettors = mk_paginator(request, bettors, PAGINATION_COUNT)

    template = "accounts/administrator/users/verified.html"
    context = {
        "bettors": bettors,
        "verified_users": verified_users,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_users_deactivated(request):
    bettors = Profile.objects.filter(
        user__is_staff=False,
        email_confirmed=True,
        user__is_active=False,
    )
    deactivated_users = bettors.count()

    bettors = mk_paginator(request, bettors, PAGINATION_COUNT)

    template = "accounts/administrator/users/deactivated.html"
    context = {
        "bettors": bettors,
        "deactivated_users": deactivated_users,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_users_detail(request, username):
    try:
        # Fetch the user's profile and actions
        profile = Profile.objects.select_related("user").get(user__username=username)
        actions = Action.objects.filter(user=profile.user).order_by("-created")[:10]

        # Fetch running groups and exclude groups the user already belongs to
        running_groups = Group.objects.running()
        user_groups = profile.user.bet_groups.all()
        eligible_groups = running_groups.exclude(
            id__in=user_groups.values_list("id", flat=True)
        )
    except Profile.DoesNotExist:
        # Handle the case where the user does not exist
        messages.error(request, "User not found.")
        return redirect("administrator:users_all")

    template = "accounts/administrator/users/detail.html"
    context = {
        "profile": profile,
        "user": profile.user,
        "actions": actions,
        "groups": eligible_groups,
        "user_groups": user_groups,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_users_assign_group(request, username):
    try:
        # Fetch the user by username
        user = get_user_model().objects.get(username=username)
    except get_user_model().DoesNotExist:
        # Handle the case where the user is not found
        messages.error(request, "User not found.")
        return redirect("administrator:users_all")

    if request.method == "POST":
        group_id = request.POST.get("group")
        if not group_id:
            # If no group is selected, show an error and redirect
            messages.error(request, "Please select a group.")
            return redirect("administrator:users_detail", username=username)

        try:
            # Check if the group exists
            group = Group.objects.get(group_id=group_id)
            if group not in user.bet_groups.all():
                # Add the user to the group if they are not already a member
                user.bet_groups.add(group)
                messages.success(
                    request,
                    f"{user.username} has been successfully added to the group '{group.name}'.",
                )
                # Send email notification
                current_site = get_current_site(request)
                protocol = "https" if request.is_secure() else "http"

                subject = render_to_string(
                    "accounts/administrator/users/emails/group_assignment_subject.txt",
                    {"site_name": current_site.name},
                ).strip()

                text_message = render_to_string(
                    "accounts/administrator/users/emails/group_assignment_email.txt",
                    {
                        "user": user,
                        "group": group.name,
                        "domain": current_site.domain,
                        "protocol": protocol,
                        "site_name": current_site.name,
                    },
                ).strip()

                html_message = render_to_string(
                    "accounts/administrator/users/emails/group_assignment_email.html",
                    {
                        "user": user,
                        "group": group.name,
                        "domain": current_site.domain,
                        "protocol": protocol,
                        "site_name": current_site.name,
                    },
                )

                # Send email asynchronously
                send_email_thread(
                    subject,
                    text_message,
                    html_message,
                    user.email,
                    user.get_full_name(),
                )

                create_action(
                    request.user,
                    "Group Assignment",
                    f"{user.username} has been assigned to the group: {group.name}",
                    target=user.profile,
                )

            else:
                # Notify if the user is already in the group
                messages.warning(
                    request, f"{user.username} is already in {group.name}."
                )
        except Group.DoesNotExist:
            # Handle the case where the group does not exist
            messages.error(request, "Invalid group selected.")

        # Redirect back to the user detail page after processing
        return redirect("administrator:users_detail", username=username)

    # For non-POST requests, simply redirect to the detail page
    return redirect("administrator:users_detail", username=username)


@login_required
@user_passes_test(is_admin)
def admin_suspend_user(request, username):
    profile = get_object_or_404(Profile, user__username=username)

    # Set the ban status on the Profile and deactivate the User
    profile.is_banned = True
    profile.user.is_active = False
    profile.save()
    profile.user.save()

    # Log the suspension action
    create_action(
        request.user,
        "User Suspension",
        f"suspended the user {profile.user.get_full_name()}",
        target=profile.user,
    )

    # Send Suspension Email
    subject = "Account Suspended"
    html_message = render_to_string(
        "accounts/administrator/users/emails/suspension_notification.html",
        {"user": profile.user},
    )
    text_message = strip_tags(html_message)
    send_email_thread(
        subject,
        text_message,
        html_message,
        profile.user.email,
        profile.user.get_full_name(),
    )

    messages.success(
        request,
        "User has been suspended and notified by email.",
    )
    return redirect("administrator:users_detail", username=username)


@login_required
@user_passes_test(is_admin)
def admin_unban_user(request, username):
    profile = get_object_or_404(Profile, user__username=username)

    profile.is_banned = False
    profile.user.is_active = True
    profile.save()
    profile.user.save()

    # Log the unban action
    create_action(
        request.user,
        "User Unbanning",
        f"unbanned the user {profile.user.get_full_name()}",
        target=profile.user,
    )

    # Send Unban Email
    subject = "Account Suspension Lifted"
    html_message = render_to_string(
        "accounts/administrator/users/emails/unban_notification.html",
        {"user": profile.user},
    )
    text_message = strip_tags(html_message)
    send_email_thread(
        subject,
        text_message,
        html_message,
        profile.user.email,
        profile.user.get_full_name(),
    )

    messages.success(
        request,
        "User has been unbanned and notified by email.",
    )
    return redirect("administrator:users_detail", username=username)


##############
# TICKETS
##############


@login_required
@user_passes_test(is_admin)
def admin_tickets_all(request):
    tickets = Ticket.objects.all()
    total_tickets = tickets.count()
    pending_tickets = tickets.filter(status=Ticket.Status.PENDING).count()
    answered_tickets = tickets.filter(status=Ticket.Status.ANSWERED).count()
    closed_tickets = tickets.filter(status=Ticket.Status.CLOSED).count()

    tickets = mk_paginator(request, tickets, PAGINATION_COUNT)

    template = "accounts/administrator/tickets/all.html"
    context = {
        "tickets": tickets,
        "total_tickets": total_tickets,
        "pending_tickets": pending_tickets,
        "answered_tickets": answered_tickets,
        "closed_tickets": closed_tickets,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_tickets_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    replies = ticket.replies.all().order_by("created")

    if request.method == "POST":
        if "reply" in request.POST:
            reply_form = TicketReplyForm(request.POST)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.ticket = ticket
                reply.user = request.user
                reply.save()
                messages.success(
                    request,
                    "Your reply to this ticket has been posted.",
                )
                # TODO: Send an email to the Bettor whenever an Admin replies
                # to the Ticket
                return redirect(
                    "administrator:tickets_detail", ticket_id=ticket.ticket_id
                )

        elif "update_status" in request.POST:
            new_status = request.POST.get("status")
            if new_status in dict(Ticket.Status.choices):
                ticket.status = new_status
                ticket.save()
                messages.success(
                    request,
                    "Ticket status updated successfully.",
                )
            else:
                messages.error(request, "Invalid status selected.")
            # TODO: Send an email to the Bettor when an Admin updates the
            # status of the Ticket.
            return redirect(
                "administrator:tickets_detail",
                ticket_id=ticket.ticket_id,
            )

    else:
        reply_form = TicketReplyForm()

    template = "accounts/administrator/tickets/detail.html"
    context = {
        "ticket": ticket,
        "replies": replies,
        "reply_form": reply_form,
    }
    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_tickets_pending(request):
    tickets = Ticket.objects.pending()
    pending_tickets = tickets.filter(status=Ticket.Status.PENDING).count()

    tickets = mk_paginator(request, tickets, PAGINATION_COUNT)

    template = "accounts/administrator/tickets/pending.html"
    context = {
        "tickets": tickets,
        "pending_tickets": pending_tickets,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_tickets_answered(request):
    tickets = Ticket.objects.answered()
    answered_tickets = tickets.filter(status=Ticket.Status.ANSWERED).count()

    template = "accounts/administrator/tickets/answered.html"
    context = {
        "tickets": tickets,
        "answered_tickets": answered_tickets,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_tickets_closed(request):
    tickets = Ticket.objects.closed()
    closed_tickets = tickets.filter(status=Ticket.Status.CLOSED).count()

    tickets = mk_paginator(request, tickets, PAGINATION_COUNT)

    template = "accounts/administrator/tickets/closed.html"
    context = {
        "tickets": tickets,
        "closed_tickets": closed_tickets,
    }

    return render(request, template, context)


###############
# WITHDRAWALS
###############


@login_required
@user_passes_test(is_admin)
def admin_withdrawals_all(request):
    """
    View all withdrawal requests, regardless of their status.
    """
    withdrawals = Withdrawal.objects.all().select_related("user", "wallet")

    # Calculate statistics
    total_withdrawals = withdrawals.count()
    pending_withdrawals = withdrawals.filter(status=Withdrawal.Status.PENDING).count()
    approved_withdrawals = withdrawals.filter(status=Withdrawal.Status.APPROVED).count()
    cancelled_withdrawals = withdrawals.filter(
        status=Withdrawal.Status.CANCELLED
    ).count()

    withdrawals = mk_paginator(request, withdrawals, PAGINATION_COUNT)

    template = "accounts/administrator/withdrawals/all.html"
    context = {
        "withdrawals": withdrawals,
        "total_withdrawals": total_withdrawals,
        "pending_withdrawals": pending_withdrawals,
        "approved_withdrawals": approved_withdrawals,
        "cancelled_withdrawals": cancelled_withdrawals,
    }

    return render(request, template, context)


def send_withdrawal_email(request, withdrawal, status):
    """
    Sends email notification to the user based on withdrawal status.
    """
    user = withdrawal.user
    current_site = get_current_site(request)
    protocol = "https" if request.is_secure() else "http"

    if status == "approved":
        subject = render_to_string(
            "accounts/administrator/withdrawals/emails/approved_subject.txt",
            {"site_name": current_site.name},
        ).strip()
        html_message = render_to_string(
            "accounts/administrator/withdrawals/emails/approved_email.html",
            {
                "user": user,
                "withdrawal": withdrawal,
                "domain": current_site.domain,
                "protocol": protocol,
                "site_name": current_site.name,
            },
        )
        text_message = render_to_string(
            "accounts/administrator/withdrawals/emails/approved_email.txt",
            {
                "user": user,
                "withdrawal": withdrawal,
                "domain": current_site.domain,
                "protocol": protocol,
                "site_name": current_site.name,
            },
        ).strip()
    elif status == "cancelled":
        subject = render_to_string(
            "accounts/administrator/withdrawals/emails/rejected_subject.txt",
            {"site_name": current_site.name},
        ).strip()
        html_message = render_to_string(
            "accounts/administrator/withdrawals/emails/rejected_email.html",
            {
                "user": user,
                "withdrawal": withdrawal,
                "domain": current_site.domain,
                "protocol": protocol,
                "site_name": current_site.name,
            },
        )
        text_message = render_to_string(
            "accounts/administrator/withdrawals/emails/rejected_email.txt",
            {
                "user": user,
                "withdrawal": withdrawal,
                "domain": current_site.domain,
                "protocol": protocol,
                "site_name": current_site.name,
            },
        ).strip()
    else:
        return  # Invalid status, do not send email

    send_email_thread(
        subject=subject,
        text_content=text_message,
        html_content=html_message,
        recipient_email=user.email,
        recipient_name=user.get_full_name(),
    )


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_process_withdrawal(request, withdrawal_id):
    """
    Handles the approval or cancellation of a withdrawal request.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("administrator:withdrawals_all")

    action = request.POST.get("action")
    note = request.POST.get("note", "")

    withdrawal = get_object_or_404(
        Withdrawal,
        withdrawal_id=withdrawal_id,
        status=Withdrawal.Status.PENDING,
    )

    try:
        with transaction.atomic():
            if action == "approve":
                # Approve withdrawal
                withdrawal.status = Withdrawal.Status.APPROVED
                withdrawal.note = note
                withdrawal.processed_at = now()

                # Deduct wallet balance
                wallet = withdrawal.wallet
                if wallet.balance < withdrawal.amount:
                    raise ValueError("Insufficient wallet balance for approval.")
                wallet.balance -= withdrawal.amount
                wallet.save()

                messages.success(request, "Withdrawal approved successfully.")
                send_withdrawal_email(request, withdrawal, "approved")

            elif action == "cancel":
                # Cancel withdrawal
                withdrawal.status = Withdrawal.Status.CANCELLED
                withdrawal.note = note
                withdrawal.processed_at = now()

                messages.success(request, "Withdrawal cancelled successfully.")
                send_withdrawal_email(request, withdrawal, "cancelled")

            else:
                messages.error(request, "Invalid action specified.")
                return redirect("administrator:withdrawals_all")

            withdrawal.save()

        return redirect("administrator:withdrawals_all")

    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        logger.error(
            f"Error processing withdrawal {withdrawal_id}: {str(e)}",
            exc_info=True,
        )
        messages.error(
            request,
            "An error occurred while processing the withdrawal.",
        )

    return redirect("administrator:withdrawals_all")


@login_required
@user_passes_test(is_admin)
def admin_withdrawals_pending(request):
    """
    View only pending withdrawal requests.
    """
    withdrawals = Withdrawal.objects.filter(status=Withdrawal.Status.PENDING)

    template = "accounts/administrator/withdrawals/pending.html"
    context = {
        "withdrawals": withdrawals,
        "pending_withdrawals": withdrawals.count(),
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_withdrawals_approved(request):
    """
    View only approved withdrawal requests.
    """
    withdrawals = Withdrawal.objects.filter(status=Withdrawal.Status.APPROVED)

    template = "accounts/administrator/withdrawals/approved.html"
    context = {
        "withdrawals": withdrawals,
        "approved_withdrawals": withdrawals.count(),
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_withdrawals_cancelled(request):
    """
    View only cancelled withdrawal requests.
    """
    withdrawals = Withdrawal.objects.filter(status=Withdrawal.Status.CANCELLED)

    template = "accounts/administrator/withdrawals/cancelled.html"
    context = {
        "withdrawals": withdrawals,
        "cancelled_withdrawals": withdrawals.count(),
    }

    return render(request, template, context)


##############
# PAYOUTS
##############


@login_required
@user_passes_test(is_admin)
def admin_payouts_all(request):
    # Query all payouts
    payouts = Payout.objects.all().select_related("user")

    # Calculate statistics
    total_payouts = payouts.count()
    pending_payouts = payouts.filter(status=Payout.Status.PENDING).count()
    approved_payouts = payouts.filter(status=Payout.Status.APPROVED).count()
    cancelled_payouts = payouts.filter(status=Payout.Status.CANCELLED).count()

    # TODO:
    # 1. Move the form into its own view
    # 2. Send an email to the Bettor when the Admin approves the Payout, including the Note
    # 3. A Payout can either be Approved or Cancelled
    # 4. Once a Payout status has been changed, it can not be reverted.
    # 5. Ability to update Payout should only be for ALL or PENDING views
    # 6. Also send email to Bettor when an Admin Cancels a Payout

    # Handle form submission for payout updates
    if request.method == "POST":
        payout_id = request.POST.get("payout_id")
        note = request.POST.get("note")

        if payout_id:
            try:
                payout = Payout.objects.get(
                    id=payout_id,
                    status=Payout.Status.PENDING,
                )
                payout.note = note
                payout.status = Payout.Status.APPROVED
                payout.paid_on = timezone.now()
                payout.save()
                messages.success(
                    request,
                    "Payout approved successfully.",
                )
                # create_action(
                #     payout.user,
                #     "Payout Wins Completed.",
                #     f"{payout.user.get_full_name} has been paid their winnings.",
                #     payout.user,
                # )
            except Payout.DoesNotExist:
                messages.error(request, "Payout not found.")

    payouts = mk_paginator(request, payouts, PAGINATION_COUNT)

    template = "accounts/administrator/payouts/all.html"
    context = {
        "payouts": payouts,
        "total_payouts": total_payouts,
        "pending_payouts": pending_payouts,
        "approved_payouts": approved_payouts,
        "cancelled_payouts": cancelled_payouts,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_payouts_pending(request):
    payouts = Payout.objects.filter(status=Payout.Status.PENDING)
    pending_payouts = payouts.count()

    template = "accounts/administrator/payouts/pending.html"
    context = {
        "payouts": payouts,
        "pending_payouts": pending_payouts,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_payouts_approved(request):
    payouts = Payout.objects.filter(status=Payout.Status.APPROVED)
    approved_payouts = payouts.count()

    template = "accounts/administrator/payouts/approved.html"
    context = {
        "payouts": payouts,
        "approved_payouts": approved_payouts,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_payouts_cancelled(request):
    payouts = Payout.objects.filter(status=Payout.Status.CANCELLED)
    cancelled_payouts = payouts.count()

    template = "accounts/administrator/payouts/cancelled.html"
    context = {
        "payouts": payouts,
        "cancelled_payouts": cancelled_payouts,
    }

    return render(request, template, context)
