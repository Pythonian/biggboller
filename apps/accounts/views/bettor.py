from django.contrib.auth.decorators import login_required
import uuid
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
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
from apps.accounts.models import Bundle, Deposit, Action, Ticket
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

    # Calculate the total of all approved/sent withdrawals

    template = "accounts/bettor/dashboard.html"
    context = {
        "bundles": bundles,
        "total_bundles": total_bundles,
        "actions": actions,
        "total_tickets": total_tickets,
        "total_deposits": total_deposits,
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
                "You updated your profile information successfully.",
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
    bundles = Bundle.objects.filter(status=Bundle.Status.PENDING)
    pending_bundles = bundles.count()

    bundles = mk_paginator(request, bundles, PAGINATION_COUNT)

    if request.method == "POST":
        bundle_id = request.POST.get("bundle_id")
        try:
            bundle = Bundle.objects.get(id=bundle_id)
        except Bundle.DoesNotExist:
            messages.success(request, f"Bundle with ID {bundle_id} does not exist.")
            return redirect("bettor:bundles_all")

        form = BundlePurchaseForm(request.POST, bundle=bundle)
        if form.is_valid():
            quantity = int(form.cleaned_data["quantity"])
            total_amount = bundle.price * quantity

            # Check if there is an existing pending deposit for this bundle
            deposit = Deposit.objects.filter(
                user=request.user,
                bundle=bundle,
                status=Deposit.Status.PENDING,
            ).first()

            if deposit:
                # Update the existing deposit if it's found
                deposit.quantity = quantity
                deposit.amount = total_amount
                deposit.save()
                messages.info(
                    request, "Your previous pending deposit has been updated."
                )
            else:
                # Generate a unique reference and create a new deposit if none exists
                reference = f"DEP-{uuid.uuid4().hex[:10].upper()}"
                deposit = Deposit.objects.create(
                    user=request.user,
                    bundle=bundle,
                    quantity=quantity,
                    amount=total_amount,
                    reference=reference,
                    status=Deposit.Status.PENDING,
                )

            return redirect("bettor:bundles_purchase", id=bundle.id)
        else:
            messages.error(
                request,
                "An error occured while submitting the form.",
            )
            # Optionally, handle form errors
            print("Form is invalid:", form.errors)
    else:
        form = BundlePurchaseForm()

    template = "accounts/bettor/bundles/all.html"
    context = {
        "bundles": bundles,
        "pending_bundles": pending_bundles,
        "form": form,
    }

    return render(request, template, context)


@login_required
def bettor_bundles_purchase(request, id):
    bundle = get_object_or_404(Bundle, id=id)

    # Fetch the pending deposit for the current user and bundle
    deposit = Deposit.objects.filter(
        user=request.user,
        bundle=bundle,
        status=Deposit.Status.PENDING,
    ).first()

    if not deposit:
        # If no deposit exists, handle it (redirect or raise error)
        messages.error(request, "No pending deposit found for this bundle.")
        return redirect("bettor:bundles_all")

    request.session["deposit_id"] = str(deposit.id)

    paystack_amount = int(deposit.amount * 100)

    paystack_ref = deposit.paystack_id or get_random_string(length=12).upper()

    if not deposit.paystack_id:
        deposit.paystack_id = paystack_ref
        deposit.save()

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
    # deposit_id = request.session.get("deposit_id")
    # deposit = get_object_or_404(Deposit, id=deposit_id)
    deposit = get_object_or_404(Deposit, paystack_id=ref)
    if deposit:
        create_action(
            deposit.user,
            "has just purchased a bundle.",
            deposit.bundle,
        )

    template = "paystack/invoice.html"
    context = {
        "deposit": deposit,
    }

    return render(request, template, context)


@csrf_exempt
def payment_cancelled(request):
    return render(request, "paystack/cancelled.html")


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
            return redirect("bettor:tickets_all")
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
