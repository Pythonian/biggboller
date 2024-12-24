from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Exists, OuterRef

from apps.core.utils import mk_paginator, create_action
from ..models import Bundle, Purchase, GroupRequest, Group

PAGINATION_COUNT = 20


##############
# GROUPS
##############


@login_required
def bettor_groups_all(request):
    """View to list all groups a user has joined."""

    groups = request.user.bet_groups.all()
    groups = mk_paginator(request, groups, PAGINATION_COUNT)

    template = "groups/bettor/all.html"
    context = {
        "groups": groups,
    }

    return render(request, template, context)


@login_required
def bettor_groups_available(request):
    # Fetch the groups the user is already a member of
    user_groups = request.user.bet_groups.all()

    # Fetch groups the user is not yet a member of and are running
    groups = (
        Group.objects.filter(status=Group.Status.RUNNING)
        .exclude(id__in=user_groups)
        .annotate(
            request_sent=Exists(
                GroupRequest.objects.filter(user=request.user, group=OuterRef("pk"))
            )
        )
    )

    # Handle group request submission
    if request.method == "POST":
        group_id = request.POST.get("group_id")
        group = get_object_or_404(Group, id=group_id, status=Group.Status.RUNNING)

        # Check if a request already exists
        if GroupRequest.objects.filter(user=request.user, group=group).exists():
            messages.error(request, "You have already requested to join this group.")
        else:
            # Create the group request
            GroupRequest.objects.create(user=request.user, group=group)
            messages.success(
                request, f"Your request to join '{group.name}' was sent successfully."
            )
            create_action(
                request.user,
                "Join Group Request",
                f"Requested to join the group: {group.name}",
                target=group,
            )

        return redirect(reverse("bettor_groups:groups_available"))

    # Render template
    template = "groups/bettor/available.html"
    context = {
        "groups": groups,
    }

    return render(request, template, context)


@login_required
def bettor_bundles_owned(request):
    purchases = Purchase.objects.filter(
        user=request.user,
        status=Purchase.Status.APPROVED,
    )
    total_purchases = purchases.count()
    purchases = mk_paginator(request, purchases, PAGINATION_COUNT)

    template = "accounts/bettor/bundles/owned.html"
    context = {
        "purchases": purchases,
        "total_purchases": total_purchases,
    }

    return render(request, template, context)


@login_required
def bettor_bundle_detail(request, bundle_id):
    """View to list the details of a bundle of a specific group a user has joined."""
    bundle = get_object_or_404(Bundle, bundle_id=bundle_id)
    # Check if the user has already purchased this bundle
    is_purchased = Purchase.objects.filter(
        user=request.user,
        bundle=bundle,
        status=Purchase.Status.APPROVED,
    ).first()

    # Determine if the bundle can be purchased
    is_purchasable = bundle.status == Bundle.Status.PENDING and not is_purchased

    template = "groups/bettor/detail.html"
    context = {
        "bundle": bundle,
        "is_purchased": is_purchased,
        "is_purchasable": is_purchasable,
    }

    return render(request, template, context)
