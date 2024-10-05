from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from apps.accounts.models import Group
from apps.accounts.forms import GroupCreateForm, GroupUpdateForm
from django.http import JsonResponse
from django.template.loader import render_to_string


def is_admin(user):
    """
    Check if the user has admin privileges.
    Adjust this function based on your authentication setup.
    """
    return user.is_staff or user.is_superuser


def admin_dashboard(request):
    template = "accounts/administrator/dashboard.html"
    context = {}

    return render(request, template, context)


##############
# GROUPS
##############


@login_required
@user_passes_test(is_admin)
def admin_groups_all(request):
    """View to list all betting groups."""

    groups = Group.objects.all()
    running_groups = groups.filter(status=Group.Status.RUNNING).count()
    closed_groups = groups.filter(status=Group.Status.CLOSED).count()

    if request.method == "POST":
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.status = Group.Status.RUNNING
            group.save()
            messages.success(
                request, f'Group "{group.name}" has been created successfully.'
            )
            return redirect("administrator:groups_all")
    else:
        form = GroupCreateForm()

    template = "accounts/administrator/groups/all.html"
    context = {
        "groups": groups,
        "running_groups": running_groups,
        "closed_groups": closed_groups,
        "form": form,
    }

    return render(request, template, context)


def admin_groups_running(request):
    groups = Group.objects.running()
    running_groups = groups.filter(status=Group.Status.RUNNING).count()

    template = "accounts/administrator/groups/running.html"
    context = {
        "groups": groups,
        "running_groups": running_groups,
    }

    return render(request, template, context)


def admin_groups_closed(request):
    groups = Group.objects.closed()
    closed_groups = groups.filter(status=Group.Status.CLOSED).count()

    template = "accounts/administrator/groups/closed.html"
    context = {
        "groups": groups,
        "closed_groups": closed_groups,
    }

    return render(request, template, context)


def admin_groups_detail(request, slug):
    template = "accounts/administrator/groups/detail.html"
    context = {}

    return render(request, template, context)


def admin_groups_new(request):
    template = "accounts/administrator/groups/new.html"
    context = {}

    return render(request, template, context)


##############
# BUNDLES
##############


def admin_bundles_pending(request):
    template = "accounts/administrator/bundles/pending.html"
    context = {}

    return render(request, template, context)


def admin_bundles_won(request):
    template = "accounts/administrator/bundles/won.html"
    context = {}

    return render(request, template, context)


def admin_bundles_lost(request):
    template = "accounts/administrator/bundles/lost.html"
    context = {}

    return render(request, template, context)


def admin_bundles_refunded(request):
    template = "accounts/administrator/bundles/refunded.html"
    context = {}

    return render(request, template, context)


def admin_bundles_all(request):
    template = "accounts/administrator/bundles/all.html"
    context = {}

    return render(request, template, context)


##############
# USERS
##############


def admin_users_all(request):
    template = "accounts/administrator/users/all.html"
    context = {}

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
    template = "accounts/administrator/tickets/all.html"
    context = {}

    return render(request, template, context)


def admin_tickets_pending(request):
    template = "accounts/administrator/tickets/pending.html"
    context = {}

    return render(request, template, context)


def admin_tickets_answered(request):
    template = "accounts/administrator/tickets/answered.html"
    context = {}

    return render(request, template, context)


def admin_tickets_closed(request):
    template = "accounts/administrator/tickets/closed.html"
    context = {}

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
