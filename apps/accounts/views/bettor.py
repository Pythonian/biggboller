from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import logout
from django.template.loader import render_to_string
from django.db.models import Sum
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password, check_password

from apps.accounts.forms import (
    BundlePurchaseForm,
    UserUpdateForm,
    ProfileUpdateForm,
    TicketCreateForm,
    TicketReplyForm,
    OnboardingForm,
    UpdateTransactionPINForm,
)
from apps.accounts.models import Action, Ticket
from apps.groups.models import Bundle, Group, Purchase, Payout
from apps.accounts.utils import create_action, send_email_thread
from apps.core.utils import mk_paginator
from apps.wallets.models import Wallet, Withdrawal, Deposit
from apps.wallets.forms import TransactionPINForm
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
def bettor_groups(request):
    pass


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


##############
# BUNDLES
##############


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
def bettor_bundles_all(request):
    # Get the groups the user is assigned to
    assigned_groups = request.user.bet_groups.all()

    # Get all bundles for the user's assigned groups that are still pending
    bundles = Bundle.objects.filter(
        status=Bundle.Status.PENDING,
        group__in=assigned_groups,
        group__status=Group.Status.RUNNING,
    )

    # Get bundles where the user has an approved purchase
    approved_bundles = Purchase.objects.filter(
        user=request.user, status=Purchase.Status.APPROVED
    ).values_list("bundle_id", flat=True)

    # Exclude bundles the user already has an approved purchase for
    bundles = bundles.exclude(id__in=approved_bundles)

    pending_bundles = bundles.count()

    # Apply pagination
    bundles = mk_paginator(request, bundles, PAGINATION_COUNT)

    template = "accounts/bettor/bundles/all.html"
    context = {
        "bundles": bundles,
        "pending_bundles": pending_bundles,
    }

    return render(request, template, context)


@login_required
def bettor_bundles_detail(request, bundle_id):
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
            return redirect("bettor:bundle_purchase_pin")

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
                            "bettor:purchase_successful",
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


##############
# TICKETS
##############


@login_required
def bettor_tickets_all(request):
    tickets = Ticket.objects.filter(user=request.user)
    total_tickets = tickets.count()
    pending_tickets = tickets.filter(status=Ticket.Status.PENDING).count()
    answered_tickets = tickets.filter(status=Ticket.Status.ANSWERED).count()
    closed_tickets = tickets.filter(status=Ticket.Status.CLOSED).count()

    # TODO: Move Ticket creation to its own view and page. Ticket should be
    # created from all the views.

    if request.method == "POST":
        form = TicketCreateForm(request.POST)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.status = Ticket.Status.PENDING
            ticket.user = request.user
            ticket.save()

            messages.success(
                request,
                f'Your Ticket with ID "#{ticket.ticket_id}" have been created successfully.',
            )
            # TODO: Send an Email to the Bettor confirming their successful Ticket creation
            create_action(
                request.user,
                "New Ticket Opened",
                "created a new ticket for resolution.",
                ticket,
            )
            return redirect(ticket)
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = TicketCreateForm()

    tickets = mk_paginator(request, tickets, PAGINATION_COUNT)

    template = "accounts/bettor/tickets/all.html"
    context = {
        "tickets": tickets,
        "total_tickets": total_tickets,
        "pending_tickets": pending_tickets,
        "answered_tickets": answered_tickets,
        "closed_tickets": closed_tickets,
        "form": form,
    }

    return render(request, template, context)


@login_required
def bettor_tickets_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    replies = ticket.replies.all().order_by("created")

    if request.method == "POST":
        if "reply" in request.POST:
            reply_form = TicketReplyForm(request.POST)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.ticket = ticket
                reply.ticket.updated = timezone.now()
                reply.user = request.user
                reply.save()
                messages.success(
                    request,
                    "Your reply to this ticket has been posted.",
                )
                create_action(
                    request.user,
                    "New Reply To Ticket",
                    "posted a new reply to their ticket.",
                    ticket,
                )
                return redirect(
                    "bettor:tickets_detail",
                    ticket_id=ticket.ticket_id,
                )

        elif "update_status" in request.POST:
            new_status = request.POST.get("status")
            if new_status in dict(Ticket.Status.choices):
                ticket.status = new_status
                ticket.updated = timezone.now()
                ticket.save()
                messages.success(
                    request,
                    "Ticket status updated successfully.",
                )
                # TODO: Send email to Bettor about their Ticket status change
                create_action(
                    request.user,
                    "Ticket Status Update",
                    f"updated the status of their ticket to {ticket.get_status_display()}.",
                    ticket,
                )
            else:
                messages.error(request, "Invalid status selected.")
            return redirect(
                "bettor:tickets_detail",
                ticket_id=ticket.ticket_id,
            )

    else:
        reply_form = TicketReplyForm()

    template = "accounts/bettor/tickets/detail.html"
    context = {
        "ticket": ticket,
        "replies": replies,
        "reply_form": reply_form,
    }
    return render(request, template, context)


@login_required
def bettor_tickets_pending(request):
    tickets = Ticket.objects.pending().filter(user=request.user)
    pending_tickets = tickets.filter(status=Ticket.Status.PENDING).count()

    tickets = mk_paginator(request, tickets, PAGINATION_COUNT)

    template = "accounts/bettor/tickets/pending.html"
    context = {
        "tickets": tickets,
        "pending_tickets": pending_tickets,
    }

    return render(request, template, context)


@login_required
def bettor_tickets_answered(request):
    tickets = Ticket.objects.answered().filter(user=request.user)
    answered_tickets = tickets.filter(status=Ticket.Status.ANSWERED).count()

    template = "accounts/bettor/tickets/answered.html"
    context = {
        "tickets": tickets,
        "answered_tickets": answered_tickets,
    }

    return render(request, template, context)


@login_required
def bettor_tickets_closed(request):
    tickets = Ticket.objects.closed().filter(user=request.user)
    closed_tickets = tickets.filter(status=Ticket.Status.CLOSED).count()

    tickets = mk_paginator(request, tickets, PAGINATION_COUNT)

    template = "accounts/bettor/tickets/closed.html"
    context = {
        "tickets": tickets,
        "closed_tickets": closed_tickets,
    }

    return render(request, template, context)


##############
# DEPOSITS
##############


@login_required
def bettor_deposits_all(request):
    deposits = Deposit.objects.filter(user=request.user)
    total_deposits = deposits.count()
    pending_deposits = deposits.filter(status=Deposit.Status.PENDING).count()
    approved_deposits = deposits.filter(status=Deposit.Status.COMPLETED).count()
    cancelled_deposits = deposits.filter(status=Deposit.Status.FAILED).count()

    deposits = mk_paginator(request, deposits, PAGINATION_COUNT)

    template = "accounts/bettor/deposits/all.html"
    context = {
        "deposits": deposits,
        "total_deposits": total_deposits,
        "pending_deposits": pending_deposits,
        "approved_deposits": approved_deposits,
        "cancelled_deposits": cancelled_deposits,
    }

    return render(request, template, context)


##############
# WITHDRAWALS
##############


@login_required
def bettor_withdrawals_all(request):
    withdrawals = Withdrawal.objects.filter(user=request.user)

    # Calculate statistics
    total_withdrawals = withdrawals.count()
    pending_withdrawals = withdrawals.filter(status=Purchase.Status.PENDING).count()
    approved_withdrawals = withdrawals.filter(status=Purchase.Status.APPROVED).count()

    withdrawals = mk_paginator(request, withdrawals, PAGINATION_COUNT)

    template = "accounts/bettor/withdrawals/all.html"
    context = {
        "withdrawals": withdrawals,
        "total_withdrawals": total_withdrawals,
        "pending_withdrawals": pending_withdrawals,
        "approved_withdrawals": approved_withdrawals,
    }

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


@login_required
def bettor_payouts_pending(request):
    payouts = Payout.objects.filter(
        status=Payout.Status.PENDING,
        user=request.user,
    )
    pending_payouts = payouts.count()

    payouts = mk_paginator(request, payouts, PAGINATION_COUNT)

    template = "accounts/bettor/payouts/pending.html"
    context = {
        "payouts": payouts,
        "pending_payouts": pending_payouts,
    }

    return render(request, template, context)


@login_required
def bettor_payouts_approved(request):
    payouts = Payout.objects.filter(
        status=Payout.Status.APPROVED,
        user=request.user,
    )
    approved_payouts = payouts.count()

    payouts = mk_paginator(request, payouts, PAGINATION_COUNT)

    template = "accounts/bettor/payouts/approved.html"
    context = {
        "payouts": payouts,
        "approved_payouts": approved_payouts,
    }

    return render(request, template, context)


@login_required
def bettor_payouts_cancelled(request):
    payouts = Payout.objects.filter(
        status=Payout.Status.CANCELLED,
        user=request.user,
    )
    cancelled_payouts = payouts.count()

    payouts = mk_paginator(request, payouts, PAGINATION_COUNT)

    template = "accounts/bettor/payouts/cancelled.html"
    context = {
        "payouts": payouts,
        "cancelled_payouts": cancelled_payouts,
    }

    return render(request, template, context)
