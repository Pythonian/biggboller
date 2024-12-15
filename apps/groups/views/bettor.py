from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from apps.core.utils import mk_paginator
from apps.groups.models import Bundle, Purchase

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
def bettor_bundle_detail(request, bundle_id):
    """View to list the details of a bundle of a specific group a user has joined."""
    bundle = get_object_or_404(Bundle, bundle_id=bundle_id)
    # Check if the user has already purchased this bundle
    is_purchased = Purchase.objects.filter(
        user=request.user,
        bundle=bundle,
        status=Purchase.Status.APPROVED,
    ).first()

    template = "groups/bettor/detail.html"
    context = {
        "bundle": bundle,
        "is_purchased": is_purchased,
    }

    return render(request, template, context)
