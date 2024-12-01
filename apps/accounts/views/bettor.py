from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import logout
from apps.accounts.forms import BundlePurchaseForm
from django.template.loader import render_to_string
from django.db.models import Sum

from apps.accounts.forms import (
    UserUpdateForm,
    ProfileUpdateForm,
    TicketCreateForm,
    TicketReplyForm,
)
from apps.accounts.models import (
    Bundle,
    Deposit,
    Action,
    Ticket,
    Group,
    Payout,
)
from apps.accounts.utils import create_action, send_email_thread
from apps.core.utils import mk_paginator
from apps.wallets.models import Wallet
import logging

logger = logging.getLogger(__name__)
PAGINATION_COUNT = 10


@login_required
def bettor_dashboard(request):
    bundles = (
        Deposit.objects.filter(user=request.user)
        .select_related("bundle", "bundle__group")
        .order_by("-created")
    )
    total_bundles = bundles.count()
    actions = Action.objects.filter(user=request.user)
    total_tickets = Ticket.objects.filter(user=request.user).count()

    # Calculate the total of all approved deposits
    total_deposits = Deposit.objects.filter(
        user=request.user,
        status=Deposit.Status.APPROVED,
    ).aggregate(total_amount=Sum("amount")).get("total_amount") or Decimal(0.00)

    # Calculate the total of all approved payouts
    total_payouts = Payout.objects.filter(
        user=request.user,
        status=Payout.Status.APPROVED,
    ).aggregate(total_amount=Sum("amount")).get("total_amount") or Decimal(0.00)

    # Calculate the total of all approved/sent withdrawals

    template = "accounts/bettor/dashboard.html"
    context = {
        "bundles": bundles,
        "total_bundles": total_bundles,
        "actions": actions,
        "total_tickets": total_tickets,
        "total_deposits": total_deposits,
        "total_payouts": total_payouts,
        "wallet_balance": request.user.wallet.balance,
    }

    return render(request, template, context)


@login_required
def bettor_profile(request):
    bettor = request.user
    actions = Action.objects.filter(user=bettor)

    template = "accounts/bettor/profile.html"
    context = {
        "bettor": bettor,
        "actions": actions,
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
            return redirect("bettor:profile")
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
    assigned_groups = request.user.bet_groups.all()
    bundles = (
        Deposit.objects.filter(
            user=request.user,
            bundle__group__in=assigned_groups,
        )
        .select_related("bundle", "bundle__group")
        .order_by("-created")
    )
    total_bundles = bundles.count()

    bundles = mk_paginator(request, bundles, PAGINATION_COUNT)

    template = "accounts/bettor/bundles/owned.html"
    context = {
        "bundles": bundles,
        "total_bundles": total_bundles,
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

    # Get bundles where the user has an approved deposit
    approved_bundles = Deposit.objects.filter(
        user=request.user, status=Deposit.Status.APPROVED
    ).values_list("bundle_id", flat=True)

    # Exclude bundles the user already has an approved deposit for
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
def bettor_bundles_detail(request, id):
    bundle = get_object_or_404(Bundle, id=id)
    wallet = get_object_or_404(Wallet, user=request.user)

    # Default quantity for confirmation
    quantity = 1
    if request.method == "POST":
        form = BundlePurchaseForm(request.POST, bundle=bundle)
        if form.is_valid():
            quantity = int(form.cleaned_data["quantity"])
            total_amount = Decimal(bundle.price) * Decimal(quantity)

            # Store quantity in session for later use
            request.session["purchase_details"] = {
                "quantity": quantity,
                "total_amount": str(total_amount),
            }
            return redirect("bettor:bundles_purchase", id=bundle.id)
        else:
            messages.error(
                request, "An error occurred while submitting the form. Try again."
            )
    else:
        form = BundlePurchaseForm(bundle=bundle)

    template = "accounts/bettor/bundles/detail.html"
    context = {
        "bundle": bundle,
        "form": form,
        "wallet_balance": wallet.balance,
    }

    return render(request, template, context)


@login_required
def bettor_bundles_purchase(request, id):
    bundle = get_object_or_404(Bundle, id=id)
    wallet = get_object_or_404(Wallet, user=request.user)

    # Retrieve purchase details from session
    purchase_details = request.session.get("purchase_details")
    if not purchase_details:
        messages.error(request, "No purchase details found. Please start over.")
        return redirect("bettor:bundles_detail", id=bundle.id)

    quantity = purchase_details["quantity"]
    total_amount = Decimal(purchase_details["total_amount"])

    if request.method == "POST":
        # Ensure sufficient wallet balance
        if wallet.balance < total_amount:
            messages.error(
                request,
                "Insufficient wallet balance. Please deposit funds to proceed.",
            )
            return redirect("bettor:bundles_detail", id=bundle.id)

        try:
            with transaction.atomic():
                # Deduct amount from wallet
                wallet.balance -= total_amount
                wallet.save()

                # Create or update a pending deposit
                deposit, created = Deposit.objects.get_or_create(
                    user=request.user,
                    bundle=bundle,
                    status=Deposit.Status.PENDING,
                    defaults={"quantity": quantity, "amount": total_amount},
                )
                if not created:
                    deposit.quantity = quantity
                    deposit.amount = total_amount

                # Approve the deposit
                deposit.status = Deposit.Status.APPROVED
                deposit.save()

                # Calculate the potential win after purchase
                potential_win = deposit.potential_win

                # Add user as a participant
                bundle.participants.add(request.user)

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

            return redirect("bettor:purchase_successful", id=deposit.id)

        except Exception as e:
            # Log the error
            logger.error(f"Error during transaction: {str(e)}", exc_info=True)

            messages.error(
                request,
                "An error occurred while processing your transaction. Try again",
            )

            return redirect("bettor:bundles_detail", id=bundle.id)

    return render(
        request,
        "accounts/bettor/bundles/purchase.html",
        {
            "bundle": bundle,
            "quantity": quantity,
            "total_amount": total_amount,
        },
    )


@login_required
def bettor_purchase_successful(request, id):
    deposit = get_object_or_404(
        Deposit, id=id, user=request.user, status=Deposit.Status.APPROVED
    )

    return render(
        request, "accounts/bettor/bundles/successful.html", {"deposit": deposit}
    )


##############
# TICKETS
##############


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


def bettor_tickets_answered(request):
    tickets = Ticket.objects.answered().filter(user=request.user)
    answered_tickets = tickets.filter(status=Ticket.Status.ANSWERED).count()

    template = "accounts/bettor/tickets/answered.html"
    context = {
        "tickets": tickets,
        "answered_tickets": answered_tickets,
    }

    return render(request, template, context)


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
    approved_deposits = deposits.filter(status=Deposit.Status.APPROVED).count()
    cancelled_deposits = deposits.filter(status=Deposit.Status.CANCELLED).count()

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


@login_required
def bettor_deposits_pending(request):
    deposits = Deposit.objects.filter(
        status=Deposit.Status.PENDING,
        user=request.user,
    )
    pending_deposits = deposits.count()

    deposits = mk_paginator(request, deposits, PAGINATION_COUNT)

    template = "accounts/bettor/deposits/pending.html"
    context = {
        "deposits": deposits,
        "pending_deposits": pending_deposits,
    }

    return render(request, template, context)


@login_required
def bettor_deposits_approved(request):
    deposits = Deposit.objects.filter(
        status=Deposit.Status.APPROVED,
        user=request.user,
    )
    approved_deposits = deposits.count()

    deposits = mk_paginator(request, deposits, PAGINATION_COUNT)

    template = "accounts/bettor/deposits/approved.html"
    context = {
        "deposits": deposits,
        "approved_deposits": approved_deposits,
    }

    return render(request, template, context)


@login_required
def bettor_deposits_cancelled(request):
    deposits = Deposit.objects.filter(
        status=Deposit.Status.CANCELLED,
        user=request.user,
    )
    cancelled_deposits = deposits.count()

    deposits = mk_paginator(request, deposits, PAGINATION_COUNT)

    template = "accounts/bettor/deposits/cancelled.html"
    context = {
        "deposits": deposits,
        "cancelled_deposits": cancelled_deposits,
    }

    return render(request, template, context)


##############
# WITHDRAWALS
##############


@login_required
def bettor_payouts_all(request):
    payouts = Payout.objects.filter(user=request.user)

    # Calculate statistics
    total_payouts = payouts.count()
    pending_payouts = payouts.filter(status=Payout.Status.PENDING).count()
    approved_payouts = payouts.filter(status=Payout.Status.APPROVED).count()

    payouts = mk_paginator(request, payouts, PAGINATION_COUNT)

    template = "accounts/bettor/payouts/all.html"
    context = {
        "payouts": payouts,
        "total_payouts": total_payouts,
        "pending_payouts": pending_payouts,
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
