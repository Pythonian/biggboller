from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.urls import reverse
from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Sum
from django.contrib.auth.hashers import make_password, check_password

from apps.accounts.forms import (
    UserUpdateForm,
    ProfileUpdateForm,
    OnboardingForm,
    UpdateTransactionPINForm,
)
from apps.accounts.models import Action
from apps.tickets.models import Ticket
from apps.groups.models import Bundle, Group, Purchase, Payout
from apps.core.utils import create_action, mk_paginator
from apps.wallets.models import Withdrawal
import logging

logger = logging.getLogger(__name__)
PAGINATION_COUNT = 10


@login_required
def onboarding_form(request):
    """
    Handles the mandatory entry of Transaction PIN and Bank Information
    for new users.
    """
    profile = request.user.profile

    if profile.transaction_pin and profile.payout_information:
        return redirect("bettor:dashboard")

    if request.method == "POST":
        form = OnboardingForm(request.POST)

        # Validate combined PIN and bank info
        transaction_pin = request.POST.get("transaction_pin", "")
        if len(transaction_pin) != 6 or not transaction_pin.isdigit():
            form.add_error(None, "Invalid PIN. Please enter a 6-digit numeric PIN.")

        if form.is_valid():
            with transaction.atomic():
                # Hash and save the transaction PIN
                profile.transaction_pin = make_password(transaction_pin)
                # Save bank information
                profile.payout_information = form.cleaned_data["payout_information"]
                profile.save()

            messages.success(
                request,
                "Your transaction PIN and bank information have been saved.",
            )
            return redirect("bettor:dashboard")
        else:
            messages.error(
                request,
                "There was an error saving your information. Please try again.",
            )
    else:
        form = OnboardingForm()

    template = "accounts/bettor/onboarding_form.html"
    context = {
        "form": form,
    }

    return render(request, template, context)


@login_required
def update_transaction_pin(request):
    profile = request.user.profile

    if request.method == "POST":
        form = UpdateTransactionPINForm(request.POST)
        if form.is_valid():
            old_pin = form.cleaned_data["old_pin"]
            new_pin = form.cleaned_data["new_pin"]
            confirm_new_pin = form.cleaned_data["confirm_new_pin"]

            # Validate old PIN
            if not check_password(old_pin, profile.transaction_pin):
                form.add_error("old_pin", "The old PIN is incorrect.")
            elif new_pin != confirm_new_pin:
                form.add_error(
                    "confirm_new_pin", "New PIN and confirmation do not match."
                )
            else:
                # Update the transaction PIN
                profile.transaction_pin = make_password(new_pin)
                profile.save()
                messages.success(
                    request, "Your transaction PIN has been updated successfully."
                )
                return redirect(reverse("bettor:dashboard"))
    else:
        form = UpdateTransactionPINForm()

    context = {"form": form}
    return render(request, "accounts/bettor/update_transaction_pin.html", context)


@login_required
def bettor_dashboard(request):
    bundles = (
        Payout.objects.filter(user=request.user)
        .select_related("bundle", "bundle__group")
        .order_by("-created")
    )
    user_groups = Group.objects.filter(bettors=request.user)
    pending_bundles = Bundle.objects.filter(
        participants=request.user,
        status=Bundle.Status.PENDING,
    ).count()
    total_bundles = bundles.count()
    actions = Action.objects.filter(user=request.user)[:5]
    total_tickets = Ticket.objects.filter(user=request.user).count()

    total_pending_withdrawals = Withdrawal.objects.filter(
        user=request.user,
        status=Withdrawal.Status.PENDING,
    ).count()

    # Calculate the total of all bundle purchases
    total_purchases = Purchase.objects.filter(
        user=request.user,
        status=Purchase.Status.APPROVED,
    ).aggregate(total_amount=Sum("amount")).get("total_amount") or Decimal("0.00")

    # Calculate the total of all winning payouts
    total_payouts = Payout.objects.filter(
        user=request.user,
        status=Payout.Status.APPROVED,
    ).aggregate(total_amount=Sum("amount")).get("total_amount") or Decimal("0.00")

    # Calculate the total of all approved/sent withdrawals

    template = "accounts/bettor/dashboard.html"
    context = {
        "bundles": bundles,
        "user_groups": user_groups,
        "total_bundles": total_bundles,
        "actions": actions,
        "total_tickets": total_tickets,
        "total_purchases": total_purchases,
        "total_payouts": total_payouts,
        "wallet_balance": request.user.wallet.balance,
        "bettor": request.user,
        "total_pending_withdrawals": total_pending_withdrawals,
        "pending_bundles": pending_bundles,
    }

    return render(request, template, context)


@login_required
def bettor_settings(request):
    user = request.user
    profile = user.profile

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(
                request,
                "Your profile has been updated successfully.",
            )
            # TODO: Send email to Bettor after their profile has been updated
            # We shouldn't let a user update their Email
            create_action(
                user,
                "User profile updated",
                "updated their profile information successfully.",
                user.profile,
            )
            return redirect("bettor:settings")
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    template = "accounts/bettor/settings.html"
    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "bettor": user,
    }

    return render(request, template, context)


@login_required
def bettor_deactivate(request):
    # TODO: Implement Account deactivation for bettors and send an email
    user = request.user
    if request.method == "POST":
        # Disable the user's password
        user.set_unusable_password()
        # Disable the user's account
        user.is_active = False
        user.save()
        logout(request)
        messages.success(
            request,
            "Your account has been successfully deactivated.",
        )
        return redirect("core:home")

    template = "accounts/bettor/deactivate.html"
    context = {}

    return render(request, template, context)


@login_required
def bettor_payouts_all(request):
    # Get all payouts for the user
    payouts = Payout.objects.filter(user=request.user).select_related("bundle")

    # Attach purchase_amount to each payout by summing user's purchases for the payout's bundle
    for payout in payouts:
        purchases = Purchase.objects.filter(user=request.user, bundle=payout.bundle)
        payout.purchase_amount = (
            purchases.aggregate(total_amount=Sum("amount"))["total_amount"] or 0
        )

    # Calculate statistics
    total_payouts = payouts.count()
    approved_payouts = payouts.filter(status=Payout.Status.APPROVED).count()

    # Paginate payouts
    payouts = mk_paginator(request, payouts, PAGINATION_COUNT)

    template = "accounts/bettor/payouts/all.html"
    context = {
        "payouts": payouts,
        "total_payouts": total_payouts,
        "approved_payouts": approved_payouts,
    }

    return render(request, template, context)
