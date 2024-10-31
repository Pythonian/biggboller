from django.contrib.auth.decorators import login_required
import uuid
from urllib.parse import urlencode
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib import messages
from django.contrib.auth import logout
from apps.accounts.forms import BundlePurchaseForm
from django.views.decorators.csrf import csrf_exempt
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
from apps.accounts.utils import create_action
from apps.core.utils import mk_paginator

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
    # Retrieve all deposits made by the user,
    # along with related bundle and group data
    bundles = (
        Deposit.objects.filter(user=request.user)
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
    # Get all bundles
    bundles = Bundle.objects.filter(
        status=Bundle.Status.PENDING,
        group__status=Group.Status.RUNNING,
    )

    # Get bundles where the user has an Approved deposit
    approved_bundles = Deposit.objects.filter(
        user=request.user, status=Deposit.Status.APPROVED
    ).values_list("bundle_id", flat=True)

    # Exclude the bundles the user has an Approved deposit for
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
    # Check if there is a deposit for this bundle and user
    deposit = (
        Deposit.objects.filter(user=request.user, bundle=bundle)
        .exclude(status=Deposit.Status.APPROVED)
        .first()
    )

    if request.method == "POST":
        form = BundlePurchaseForm(request.POST, bundle=bundle)
        if form.is_valid():
            quantity = int(form.cleaned_data["quantity"])
            total_amount = bundle.price * quantity

            # Check if there's already a pending deposit for this user and bundle
            deposit, created = Deposit.objects.get_or_create(
                user=request.user,
                bundle=bundle,
                status=Deposit.Status.PENDING,
                defaults={
                    "quantity": quantity,
                    "amount": total_amount,
                },
            )

            # Update quantity and amount if deposit already exists but differs
            if not created and (
                deposit.quantity != quantity or deposit.amount != total_amount
            ):
                deposit.quantity = quantity
                deposit.amount = total_amount
                deposit.save()

            request.session["deposit_id"] = str(deposit.id)

            return redirect("bettor:bundles_purchase", id=bundle.id)
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
        "deposit": deposit,
    }

    return render(request, template, context)


@login_required
def bettor_bundles_purchase(request, id):
    bundle = get_object_or_404(Bundle, id=id)
    deposit_id = request.session.get("deposit_id")
    deposit = get_object_or_404(
        Deposit,
        id=deposit_id,
        bundle=bundle,
        user=request.user,
        status=Deposit.Status.PENDING,
    )

    # Paystack amount in kobo
    paystack_amount = int(deposit.amount * 100)

    # Generate the Paystack reference if it doesn't already exist
    paystack_ref = deposit.paystack_id or get_random_string(length=12).upper()
    if not deposit.paystack_id:
        deposit.paystack_id = paystack_ref
        deposit.save()

    # Create the Paystack redirect URL for after payment
    # paystack_redirect_url = "{}?{}".format(
    #     reverse("paystack:verify_payment", args=[paystack_ref]),
    #     urlencode({"amount": paystack_amount}),
    # )
    paystack_redirect_url = "{}?amount={}".format(
        reverse("paystack:verify_payment", args=[paystack_ref]),
        paystack_amount,
    )

    template = "accounts/bettor/bundles/purchase.html"
    context = {
        "bundle": bundle,
        "deposit": deposit,
        "paystack_key": settings.PAYSTACK_PUBLIC_KEY,
        "paystack_amount": paystack_amount,
        "paystack_ref": paystack_ref,
        "paystack_redirect_url": paystack_redirect_url,
    }

    return render(request, template, context)


@csrf_exempt
def payment_done(request, ref):
    deposit = get_object_or_404(Deposit, paystack_id=ref)

    if deposit.status == Deposit.Status.APPROVED:
        if request.user.is_authenticated:
            messages.success(
                request,
                f"Payment successful! Your purchase of {deposit.quantity} bundle(s) for {deposit.bundle.name} is complete.",
            )
        return redirect("bettor:bundles_detail", id=deposit.bundle.id)
    else:
        if request.user.is_authenticated:
            messages.error(
                request, "There was an issue with your payment. Please contact support."
            )
        return redirect("bettor:bundles_detail", id=deposit.bundle.id)


# @csrf_exempt
# def payment_done(request, ref):
#     # Fetch the Deposit using the paystack_id
#     deposit = get_object_or_404(Deposit, paystack_id=ref)
#     print(f"deposit - {deposit}")

#     if deposit.status == Deposit.Status.APPROVED:
#         # Add success message
#         messages.success(
#             request,
#             f"Payment successful! Your purchase of {deposit.quantity} bundle(s) for {deposit.bundle.name} is complete.",
#         )

#         # Redirect to bundles_detail view with the bundle ID
#         try:
#             return redirect("bettor:bundles_detail", id=deposit.bundle.id)
#         except AttributeError:
#             messages.error(request, "Invalid deposit or bundle.")
#             return redirect("bettor:bundles_overview")
#         # return redirect("bettor:bundles_detail", id=deposit.bundle.id)
#     else:
#         # Handle the case where payment was not successful
#         messages.error(
#             request, "There was an issue with your payment. Please contact support."
#         )
#         return redirect("bettor:bundles_detail", id=deposit.bundle.id)


@csrf_exempt
def payment_cancelled(request):
    return render(request, "paystack/failed-page.html")


##############
# TICKETS
##############


def bettor_tickets_all(request):
    tickets = Ticket.objects.filter(user=request.user)
    total_tickets = tickets.count()
    pending_tickets = tickets.filter(status=Ticket.Status.PENDING).count()
    answered_tickets = tickets.filter(status=Ticket.Status.ANSWERED).count()
    closed_tickets = tickets.filter(status=Ticket.Status.CLOSED).count()

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
# PAYOUTS
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
