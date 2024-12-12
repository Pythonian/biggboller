import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.template.loader import render_to_string
from django.db import transaction
from django.utils.crypto import get_random_string

from apps.core.utils import mk_paginator, create_action, send_email_thread

from .models import Group, Bundle, Purchase, Payout
from .forms import GroupCreateForm, GroupUpdateForm, BundleCreateForm

logger = logging.getLogger(__name__)

PAGINATION_COUNT = 20


def is_admin(user):
    """
    Check if the user has admin privileges.
    Adjust this function based on your authentication setup.
    """
    return user.is_staff or user.is_superuser


##############
# GROUPS
##############


@login_required
@user_passes_test(is_admin)
def admin_groups_all(request):
    """View to list all groups."""

    groups = Group.objects.all()
    total_groups = groups.count()
    running_groups = groups.filter(status=Group.Status.RUNNING).count()
    closed_groups = groups.filter(status=Group.Status.CLOSED).count()

    groups = mk_paginator(request, groups, PAGINATION_COUNT)

    template = "groups/all.html"
    context = {
        "groups": groups,
        "total_groups": total_groups,
        "running_groups": running_groups,
        "closed_groups": closed_groups,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_groups_new(request):
    """View to create a new group and its bundle."""

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
                    "New Group successfully created.",
                )

                create_action(
                    request.user,
                    "New Group Creation",
                    f"created a new group: {group.name}",
                    target=group,
                )
                return redirect(group)
            except Exception as e:
                logger.error(
                    f"An error occurred while creating the Group and Bundle: {str(e)}"
                )
                messages.error(
                    request,
                    "An error occurred while creating the Group and Bundle. Try again!",
                )
        else:
            messages.error(
                request,
                "Please correct the errors below.",
            )
    else:
        group_form = GroupCreateForm(prefix="group")
        bundle_form = BundleCreateForm(prefix="bundle")

    template = "groups/new.html"
    context = {
        "group_form": group_form,
        "bundle_form": bundle_form,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_groups_running(request):
    groups = Group.objects.running()
    running_groups = groups.filter(status=Group.Status.RUNNING).count()
    groups = mk_paginator(request, groups, PAGINATION_COUNT)

    template = "groups/running.html"
    context = {
        "groups": groups,
        "running_groups": running_groups,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_groups_closed(request):
    groups = Group.objects.closed()
    closed_groups = groups.filter(status=Group.Status.CLOSED).count()
    groups = mk_paginator(request, groups, PAGINATION_COUNT)

    template = "groups/closed.html"
    context = {
        "groups": groups,
        "closed_groups": closed_groups,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_groups_detail(request, group_id):
    group = get_object_or_404(Group, group_id=group_id)
    members = group.bettors.all()

    if request.method == "POST":
        form = GroupUpdateForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "This group has been updated successfully.",
            )
            create_action(
                request.user,
                "Group Update",
                f"updated the group: {group.name}",
                target=group,
            )
            return redirect(group)
    else:
        form = GroupUpdateForm(instance=group)

    template = "groups/detail.html"
    context = {
        "group": group,
        "form": form,
        "members": members,
    }

    return render(request, template, context)


##############
# BUNDLES
##############


@login_required
@user_passes_test(is_admin)
def admin_bundles_all(request):
    bundles = Bundle.objects.all()
    total_bundles = bundles.count()
    pending_bundles = bundles.filter(status=Bundle.Status.PENDING).count()
    won_bundles = bundles.filter(status=Bundle.Status.WON).count()
    lost_bundles = bundles.filter(status=Bundle.Status.LOST).count()

    bundles = mk_paginator(request, bundles, PAGINATION_COUNT)

    template = "bundles/all.html"
    context = {
        "bundles": bundles,
        "total_bundles": total_bundles,
        "pending_bundles": pending_bundles,
        "won_bundles": won_bundles,
        "lost_bundles": lost_bundles,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_bundles_pending(request):
    bundles = Bundle.objects.pending()
    pending_bundles = bundles.filter(status=Bundle.Status.PENDING).count()

    bundles = mk_paginator(request, bundles, PAGINATION_COUNT)

    template = "bundles/pending.html"
    context = {
        "bundles": bundles,
        "pending_bundles": pending_bundles,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_bundles_won(request):
    bundles = Bundle.objects.won()
    won_bundles = bundles.filter(status=Bundle.Status.WON).count()

    bundles = mk_paginator(request, bundles, PAGINATION_COUNT)

    template = "bundles/won.html"
    context = {
        "bundles": bundles,
        "won_bundles": won_bundles,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_bundles_lost(request):
    bundles = Bundle.objects.lost()
    lost_bundles = bundles.filter(status=Bundle.Status.LOST).count()

    bundles = mk_paginator(request, bundles, PAGINATION_COUNT)

    template = "bundles/lost.html"
    context = {
        "bundles": bundles,
        "lost_bundles": lost_bundles,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_bundles_detail(request, bundle_id):
    bundle = get_object_or_404(Bundle, bundle_id=bundle_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Bundle.Status.choices):
            bundle.status = new_status
            bundle.save()

            # Check if the new status is "Won" and credit the users' wallets
            if new_status == Bundle.Status.WON:
                # Iterate over participants and calculate their potential win
                for purchase in bundle.purchases.filter(
                    status=Purchase.Status.APPROVED
                ):
                    potential_win_amount = purchase.payout_amount

                    try:
                        # Credit the user's wallet with the potential win amount
                        wallet = purchase.user.wallet
                        reference = get_random_string(length=12).upper()
                        wallet.update_balance(
                            potential_win_amount,
                            transaction_type="Bundle Payout",
                            transaction_id=reference,
                        )

                        _ = Payout.objects.create(
                            user=purchase.user,
                            bundle=bundle,
                            amount=potential_win_amount,
                        )

                        # Send confirmation email
                        email_context = {
                            "user": purchase.user,
                            "bundle": bundle,
                            "amount": potential_win_amount,
                        }
                        subject = "Congratulations! Bundle Winning Payout"
                        html_content = render_to_string(
                            "accounts/bettor/bundles/email/payout.html",
                            email_context,
                        )
                        text_content = render_to_string(
                            "accounts/bettor/bundles/email/payout.txt",
                            email_context,
                        )
                        send_email_thread(
                            subject=subject,
                            text_content=text_content,
                            html_content=html_content,
                            recipient_email=purchase.user.email,
                            recipient_name=purchase.user.get_full_name(),
                        )

                        create_action(
                            request.user,
                            "Bundle Winning Payout",
                            f"{purchase.user} has been paid their bundle wins.",
                            target=purchase.user.profile,
                        )
                    except Exception as e:
                        logger.error(
                            f"Error processing payout for {purchase.user}: {e}"
                        )
                        messages.error(
                            request,
                            f"An error occurred while processing winnings for {purchase.user}.",
                        )
                        continue

            elif new_status == Bundle.Status.LOST:
                # Handle bundle lost scenario
                for purchase in bundle.purchases.filter(
                    status=Purchase.Status.APPROVED
                ):
                    try:
                        # Create a Payout record (Cancelled)
                        Payout.objects.create(
                            user=purchase.user,
                            bundle=bundle,
                            amount=0,
                            status=Payout.Status.CANCELLED,
                        )

                        # Send losing notification email
                        email_context = {
                            "user": purchase.user,
                            "bundle": bundle,
                        }
                        subject = "Bundle Result: Lost"
                        html_content = render_to_string(
                            "accounts/bettor/bundles/email/lost.html",
                            email_context,
                        )
                        text_content = render_to_string(
                            "accounts/bettor/bundles/email/lost.txt",
                            email_context,
                        )
                        send_email_thread(
                            subject=subject,
                            text_content=text_content,
                            html_content=html_content,
                            recipient_email=purchase.user.email,
                            recipient_name=purchase.user.get_full_name(),
                        )

                        create_action(
                            request.user,
                            "Bundle Lost Notification",
                            f"{purchase.user} has been notified of the lost bundle.",
                            target=purchase.user.profile,
                        )
                    except Exception as e:
                        logger.error(
                            f"Error processing lost notification for {purchase.user}: {e}"
                        )
                        messages.error(
                            request,
                            f"An error occurred while notifying {purchase.user} about the lost bundle.",
                        )
                        continue

            messages.success(request, "Bundle status updated successfully.")
            return redirect(bundle)
        else:
            messages.error(request, "Invalid status selected.")

    # Get all purchases that are approved for this bundle
    approved_purchases = bundle.purchases.filter(status=Purchase.Status.APPROVED)

    template = "bundles/detail.html"
    context = {
        "bundle": bundle,
        "approved_purchases": approved_purchases,
    }

    return render(request, template, context)
