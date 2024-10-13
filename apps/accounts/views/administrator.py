from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from apps.accounts.models import Group, Bundle, Ticket, Profile, Action
from apps.accounts.forms import (
    GroupCreateForm,
    GroupUpdateForm,
    BundleCreateForm,
    TicketReplyForm,
)
from apps.core.utils import mk_paginator

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
    }

    return render(request, template, context)


##############
# GROUPS
##############


# @login_required
# @user_passes_test(is_admin)
def admin_groups_all(request):
    """View to list all betting groups."""

    groups = Group.objects.all()
    total_groups = groups.count()
    running_groups = groups.filter(status=Group.Status.RUNNING).count()
    closed_groups = groups.filter(status=Group.Status.CLOSED).count()

    if request.method == "POST":
        group_form = GroupCreateForm(request.POST, prefix="group")
        bundle_form = BundleCreateForm(request.POST, prefix="bundle")

        if group_form.is_valid() and bundle_form.is_valid():
            try:
                with transaction.atomic():
                    # Save Group
                    group = group_form.save(commit=False)
                    group.status = Group.Status.RUNNING
                    group.save()

                    # Save Bundle
                    bundle = bundle_form.save(commit=False)
                    bundle.group = group
                    bundle.status = Bundle.Status.PENDING
                    bundle.save()

                messages.success(
                    request,
                    f'Group "{group.name}" and its Bundle "{bundle.name}" have been created successfully.',
                )
                return redirect("administrator:groups_all")
            except Exception as e:
                messages.error(
                    request,
                    f"An error occurred while creating the Group and Bundle: {str(e)}",
                )
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        group_form = GroupCreateForm(prefix="group")
        bundle_form = BundleCreateForm(prefix="bundle")

    groups = mk_paginator(request, groups, PAGINATION_COUNT)

    template = "accounts/administrator/groups/all.html"
    context = {
        "groups": groups,
        "total_groups": total_groups,
        "running_groups": running_groups,
        "closed_groups": closed_groups,
        "group_form": group_form,
        "bundle_form": bundle_form,
    }

    return render(request, template, context)


def admin_groups_running(request):
    groups = Group.objects.running()
    running_groups = groups.filter(status=Group.Status.RUNNING).count()
    groups = mk_paginator(request, groups, PAGINATION_COUNT)

    template = "accounts/administrator/groups/running.html"
    context = {
        "groups": groups,
        "running_groups": running_groups,
    }

    return render(request, template, context)


def admin_groups_closed(request):
    groups = Group.objects.closed()
    closed_groups = groups.filter(status=Group.Status.CLOSED).count()
    groups = mk_paginator(request, groups, PAGINATION_COUNT)

    template = "accounts/administrator/groups/closed.html"
    context = {
        "groups": groups,
        "closed_groups": closed_groups,
    }

    return render(request, template, context)


def admin_groups_detail(request, id):
    group = get_object_or_404(Group, id=id)

    if request.method == "POST":
        form = GroupUpdateForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "This group has been updated successfully.",
            )
            return redirect(group)
    else:
        form = GroupUpdateForm(instance=group)

    template = "accounts/administrator/groups/detail.html"
    context = {
        "group": group,
        "form": form,
    }

    return render(request, template, context)


def admin_groups_new(request):
    template = "accounts/administrator/groups/new.html"
    context = {}

    return render(request, template, context)


##############
# BUNDLES
##############


def admin_bundles_all(request):
    bundles = Bundle.objects.all()
    total_bundles = bundles.count()
    pending_bundles = bundles.filter(status=Bundle.Status.PENDING).count()
    won_bundles = bundles.filter(status=Bundle.Status.WON).count()
    lost_bundles = bundles.filter(status=Bundle.Status.LOST).count()

    bundles = mk_paginator(request, bundles, PAGINATION_COUNT)

    template = "accounts/administrator/bundles/all.html"
    context = {
        "bundles": bundles,
        "total_bundles": total_bundles,
        "pending_bundles": pending_bundles,
        "won_bundles": won_bundles,
        "lost_bundles": lost_bundles,
    }

    return render(request, template, context)


def admin_bundles_pending(request):
    bundles = Bundle.objects.pending()
    pending_bundles = bundles.filter(status=Bundle.Status.PENDING).count()

    bundles = mk_paginator(request, bundles, PAGINATION_COUNT)

    template = "accounts/administrator/bundles/pending.html"
    context = {
        "bundles": bundles,
        "pending_bundles": pending_bundles,
    }

    return render(request, template, context)


def admin_bundles_won(request):
    bundles = Bundle.objects.won()
    won_bundles = bundles.filter(status=Bundle.Status.WON).count()

    bundles = mk_paginator(request, bundles, PAGINATION_COUNT)

    template = "accounts/administrator/bundles/won.html"
    context = {
        "bundles": bundles,
        "won_bundles": won_bundles,
    }

    return render(request, template, context)


def admin_bundles_lost(request):
    bundles = Bundle.objects.lost()
    lost_bundles = bundles.filter(status=Bundle.Status.LOST).count()

    bundles = mk_paginator(request, bundles, PAGINATION_COUNT)

    template = "accounts/administrator/bundles/lost.html"
    context = {
        "bundles": bundles,
        "lost_bundles": lost_bundles,
    }

    return render(request, template, context)


def admin_bundles_detail(request, id):
    bundle = get_object_or_404(Bundle, id=id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Bundle.Status.choices):
            bundle.status = new_status
            bundle.save()
            messages.success(request, "Bundle status updated successfully.")
            return redirect(bundle)
        else:
            messages.error(request, "Invalid status selected.")

    template = "accounts/administrator/bundles/detail.html"
    context = {
        "bundle": bundle,
    }

    return render(request, template, context)


##############
# USERS
##############


def admin_users_all(request):
    bettors = Profile.objects.filter(user__is_staff=False)
    registered_users = bettors.count()
    active_users = bettors.filter(email_confirmed=True).count()
    banned_users = bettors.filter(is_banned=True).count()
    deactivated_users = bettors.filter(user__is_active=False).count()
    verified_users = bettors.filter(verified_account=True).count()
    unverified_users = bettors.filter(verified_account=False).count()

    bettors = mk_paginator(request, bettors, PAGINATION_COUNT)

    template = "accounts/administrator/users/all.html"
    context = {
        "bettors": bettors,
        "registered_users": registered_users,
        "deactivated_users": deactivated_users,
        "active_users": active_users,
        "banned_users": banned_users,
        "verified_users": verified_users,
        "unverified_users": unverified_users,
    }

    return render(request, template, context)


def admin_users_active(request):
    template = "accounts/administrator/users/active.html"
    context = {}

    return render(request, template, context)


def admin_users_banned(request):
    template = "accounts/administrator/users/banned.html"
    context = {}

    return render(request, template, context)


def admin_users_unverified(request):
    template = "accounts/administrator/users/unverified.html"
    context = {}

    return render(request, template, context)


def admin_users_verified(request):
    template = "accounts/administrator/users/verified.html"
    context = {}

    return render(request, template, context)


def admin_users_deactivated(request):
    template = "accounts/administrator/users/deactivated.html"
    context = {}

    return render(request, template, context)


################
# NOTIFICATIONS
################


def admin_users_notifications(request):
    template = "accounts/administrator/users/notifications.html"
    context = {}

    return render(request, template, context)


##############
# TICKETS
##############


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
                return redirect(
                    "administrator:tickets_detail", ticket_id=ticket.ticket_id
                )

        elif "update_status" in request.POST:
            new_status = request.POST.get("status")
            if new_status in dict(Ticket.Status.choices):
                ticket.status = new_status
                ticket.save()
                messages.success(request, "Ticket status updated successfully.")
            else:
                messages.error(request, "Invalid status selected.")
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


# def admin_tickets_detail(request, ticket_id):
#     ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
#     replies = ticket.replies.all().order_by("created")

#     if request.method == "POST":
#         if "reply" in request.POST:
#             reply_form = TicketReplyForm(request.POST)
#             if reply_form.is_valid():
#                 reply = reply_form.save(commit=False)
#                 reply.ticket = ticket
#                 reply.user = request.user
#                 reply.save()
#                 messages.success(
#                     request,
#                     "Your reply to this ticket has been posted.",
#                 )
#                 return redirect(
#                     "administrator:tickets_detail",
#                     ticket_id=ticket.ticket_id,
#                 )
#         elif "update_status" in request.POST:
#             new_status = request.POST.get("status")
#             if new_status in dict(Ticket.Status.choices):
#                 ticket.status = new_status
#                 ticket.save()
#                 messages.success(request, "Ticket status updated successfully.")
#                 return redirect(ticket)
#             else:
#                 messages.error(request, "Invalid status selected.")
#         # elif "update_status" in request.POST:
#         #     status_form = TicketStatusForm(request.POST)
#         #     if status_form.is_valid():
#         #         new_status = status_form.cleaned_data["status"]
#         #         if new_status in dict(Ticket.STATUS_CHOICES).keys():
#         #             ticket.status = new_status
#         #             ticket.save()
#         #             messages.success(request, f"Ticket status updated to {new_status}.")
#         #         return redirect("admin_ticket_detail", ticket_id=ticket.ticket_id)
#     else:
#         reply_form = TicketReplyForm()
#         # status_form = TicketStatusForm()

#     template = "accounts/administrator/tickets/detail.html"
#     context = {
#         "ticket": ticket,
#         "replies": replies,
#         "reply_form": reply_form,
#         # "status_form": status_form,
#     }
#     return render(request, template, context)


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


def admin_tickets_answered(request):
    tickets = Ticket.objects.answered()
    answered_tickets = tickets.filter(status=Ticket.Status.ANSWERED).count()

    template = "accounts/administrator/tickets/answered.html"
    context = {
        "tickets": tickets,
        "answered_tickets": answered_tickets,
    }

    return render(request, template, context)


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


##############
# DEPOSITS
##############


def admin_deposits_all(request):
    template = "accounts/administrator/deposits/all.html"
    context = {}

    return render(request, template, context)


def admin_deposits_pending(request):
    template = "accounts/administrator/deposits/pending.html"
    context = {}

    return render(request, template, context)


def admin_deposits_approved(request):
    template = "accounts/administrator/deposits/approved.html"
    context = {}

    return render(request, template, context)


def admin_deposits_rejected(request):
    template = "accounts/administrator/deposits/rejected.html"
    context = {}

    return render(request, template, context)


##############
# WITHDRAWALS
##############


def admin_withdrawals_all(request):
    template = "accounts/administrator/withdrawals/all.html"
    context = {}

    return render(request, template, context)


def admin_withdrawals_pending(request):
    template = "accounts/administrator/withdrawals/pending.html"
    context = {}

    return render(request, template, context)


def admin_withdrawals_approved(request):
    template = "accounts/administrator/withdrawals/approved.html"
    context = {}

    return render(request, template, context)


def admin_withdrawals_rejected(request):
    template = "accounts/administrator/withdrawals/rejected.html"
    context = {}

    return render(request, template, context)
