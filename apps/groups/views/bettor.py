from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Exists, OuterRef
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from django.contrib.auth.hashers import check_password
from django.db import transaction

from apps.accounts.forms import BundlePurchaseForm
from apps.core.utils import mk_paginator, create_action, send_email_thread
from ..models import Bundle, Purchase, GroupRequest, Group
from apps.wallets.models import Wallet
from apps.wallets.forms import TransactionPINForm
import logging

logger = logging.getLogger(__name__)

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

    # Check if the user is already a participant
    is_participant = request.user in bundle.participants.all()

    # Determine if the bundle can be purchased
    is_purchasable = (
        bundle.status == Bundle.Status.PENDING
        and not is_purchased
        and (bundle.current_round == 1 or is_participant)
    )

    template = "groups/bettor/detail.html"
    context = {
        "bundle": bundle,
        "is_purchased": is_purchased,
        "is_purchasable": is_purchasable,
    }

    return render(request, template, context)


@login_required
def bettor_bundles_purchase(request, bundle_id):
    bundle = get_object_or_404(Bundle, bundle_id=bundle_id)
    wallet = get_object_or_404(Wallet, user=request.user)

    # Restrict purchase for bundles marked as WON or LOST
    if bundle.status in {Bundle.Status.WON, Bundle.Status.LOST}:
        messages.error(
            request,
            f"The bundle '{bundle.name}' is no longer available for purchase.",
        )
        return redirect("bettor:dashboard")

    # Check if the user has already purchased this bundle
    purchased_bundle = Purchase.objects.filter(
        user=request.user,
        bundle=bundle,
        status=Purchase.Status.APPROVED,
    ).exists()

    # Check if the user is a participant for subsequent rounds
    is_participant = request.user in bundle.participants.all()

    # Restrict purchase if it's not the first round and the user is not a participant
    if bundle.current_round > 1 and not is_participant:
        messages.error(
            request,
            "You cannot purchase this bundle because you did not participate in earlier rounds.",
        )
        return redirect("bettor:dashboard")

    # Calculate the minimum required balance
    min_required_balance = Decimal(bundle.price) * Decimal(bundle.min_bundles_per_user)
    has_sufficient_funds = wallet.balance >= min_required_balance

    if request.method == "POST":
        form = BundlePurchaseForm(request.POST, bundle=bundle)
        if form.is_valid():
            quantity = int(form.cleaned_data["quantity"])
            total_amount = Decimal(bundle.price) * Decimal(quantity)

            if wallet.balance < total_amount:
                messages.error(
                    request,
                    "Insufficient wallet balance. Please deposit funds to proceed.",
                )
                return redirect("bettor:wallet_deposit")

            # Store bundle purchase details in session temporarily
            request.session["bundle_purchase_data"] = {
                "bundle_id": str(bundle.bundle_id),
                "quantity": quantity,
                "total_amount": str(total_amount),
                "bundle_name": bundle.name,
                "winning_percentage": str(bundle.winning_percentage),
            }
            return redirect("bettor_groups:bundle_purchase_pin")

        else:
            messages.error(
                request,
                "An error occurred while submitting the form. Try again.",
            )
    else:
        form = BundlePurchaseForm(bundle=bundle)

    template = "accounts/bettor/bundles/detail.html"
    context = {
        "bundle": bundle,
        "form": form,
        "wallet_balance": wallet.balance,
        "purchased_bundle": purchased_bundle,
        "has_sufficient_funds": has_sufficient_funds,
    }

    return render(request, template, context)


@login_required
def bettor_bundle_purchase_pin(request):
    """Handles transaction PIN verification for bundle purchases."""
    profile = request.user.profile

    # Ensure bundle purchase data exists in session
    purchase_data = request.session.get("bundle_purchase_data")
    if not purchase_data:
        messages.error(request, "Invalid purchase request.")
        return redirect("bettor:dashboard")

    bundle = get_object_or_404(Bundle, bundle_id=purchase_data["bundle_id"])
    wallet = get_object_or_404(Wallet, user=request.user)

    # Restrict purchase for bundles marked as WON or LOST
    if bundle.status in {Bundle.Status.WON, Bundle.Status.LOST}:
        messages.error(
            request,
            f"The bundle '{bundle.name}' is no longer available for purchase.",
        )
        return redirect("bettor:dashboard")

    if request.method == "POST":
        form = TransactionPINForm(request.POST)
        if form.is_valid():
            entered_pin = form.cleaned_data["transaction_pin"]

            # Verify transaction PIN
            if not check_password(entered_pin, profile.transaction_pin):
                form.add_error("transaction_pin", "Incorrect Transaction PIN.")
            else:
                try:
                    with transaction.atomic():
                        # Retrieve purchase details
                        quantity = int(purchase_data["quantity"])
                        total_amount = Decimal(purchase_data["total_amount"])
                        winning_percentage = Decimal(
                            purchase_data["winning_percentage"]
                        )

                        # Deduct amount from wallet
                        if wallet.balance < total_amount:
                            messages.error(request, "Insufficient wallet balance.")
                            return redirect("bettor:wallet_deposit")

                        wallet.balance -= total_amount
                        wallet.save()

                        # Calculate the potential win (payout amount)
                        payout_amount_interest = total_amount * (
                            winning_percentage / 100
                        )
                        payout_amount = total_amount + payout_amount_interest

                        # Create the purchase
                        purchase = Purchase.objects.create(
                            user=request.user,
                            bundle=bundle,
                            quantity=quantity,
                            amount=total_amount,
                            payout_amount=payout_amount,
                            status=Purchase.Status.APPROVED,
                            reference=get_random_string(length=12).upper(),
                        )

                        # Add user as a participant
                        bundle.participants.add(request.user)

                        # Clear session data
                        del request.session["bundle_purchase_data"]

                        # Send confirmation email
                        email_context = {
                            "user": request.user,
                            "bundle": bundle,
                            "quantity": quantity,
                            "total_amount": total_amount,
                        }
                        subject = f"Bundle Purchase Confirmation - {bundle.name}"
                        html_content = render_to_string(
                            "accounts/bettor/bundles/email/acknowledgment.html",
                            email_context,
                        )
                        text_content = render_to_string(
                            "accounts/bettor/bundles/email/acknowledgment.txt",
                            email_context,
                        )
                        send_email_thread(
                            subject=subject,
                            text_content=text_content,
                            html_content=html_content,
                            recipient_email=request.user.email,
                            recipient_name=request.user.get_full_name(),
                        )

                        # Log action
                        create_action(
                            request.user,
                            "Bundle Purchase",
                            f"purchased the bundle {bundle.name} for ₦{total_amount}.",
                            target=request.user.profile,
                        )

                        return redirect(
                            "bettor_groups:purchase_successful",
                            purchase_id=purchase.purchase_id,
                        )
                except Exception as e:
                    logger.error(f"Error during transaction: {str(e)}", exc_info=True)
                    messages.error(
                        request,
                        "An error occurred while processing your purchase. Try again.",
                    )
    else:
        form = TransactionPINForm()

    template = "accounts/bettor/bundles/purchase_pin.html"
    context = {
        "form": form,
        "purchase_data": purchase_data,
    }

    return render(request, template, context)


@login_required
def bettor_purchase_successful(request, purchase_id):
    purchase = get_object_or_404(
        Purchase,
        purchase_id=purchase_id,
        user=request.user,
        status=Purchase.Status.APPROVED,
    )

    template = "accounts/bettor/bundles/successful.html"
    context = {"purchase": purchase}

    return render(request, template, context)
