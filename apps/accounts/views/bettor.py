from django.contrib.auth.decorators import login_required
import uuid
import requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import logout
from apps.accounts.forms import BundlePurchaseForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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
    template = "accounts/bettor/dashboard.html"
    context = {}

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
def bettor_bundles_all(request):
    bundles = Bundle.objects.filter(status=Bundle.Status.PENDING)
    pending_bundles = bundles.count()

    bundles = mk_paginator(request, bundles, PAGINATION_COUNT)

    if request.method == "POST":
        bundle_id = request.POST.get("bundle_id")
        try:
            bundle = Bundle.objects.get(id=bundle_id)
        except Bundle.DoesNotExist:
            # Handle the case where the bundle does not exist
            print(f"Bundle with ID {bundle_id} does not exist.")
            return redirect("bettor:bundles_all")

        form = BundlePurchaseForm(request.POST, bundle=bundle)
        if form.is_valid():
            quantity = int(form.cleaned_data["quantity"])
            total_amount = bundle.price * quantity
            # Generate a unique reference
            reference = f"DEP-{uuid.uuid4().hex[:10].upper()}"
            # Create a Deposit instance
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
    deposit = get_object_or_404(Deposit, bundle=bundle)

    template = "accounts/bettor/bundles/purchase.html"
    context = {
        "bundle": bundle,
        "deposit": deposit,
    }

    return render(request, template, context)


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


class PurchaseBundleView(View):
    template_name = "accounts/bettor/purchase_bundle.html"

    def get(self, request):
        form = BundlePurchaseForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = BundlePurchaseForm(request.POST)
        if form.is_valid():
            bundle = form.cleaned_data["bundle"]
            quantity = form.cleaned_data["quantity"]
            total_amount = bundle.price * quantity

            # Generate a unique reference
            reference = f"DEP-{uuid.uuid4().hex[:10].upper()}"

            # Create a Deposit instance
            deposit = Deposit.objects.create(
                user=request.user,
                bundle=bundle,
                quantity=quantity,
                amount=total_amount,
                reference=reference,
                status=Deposit.Status.PENDING,
            )

            # Initialize Paystack payment
            paystack_url = "https://api.paystack.co/transaction/initialize"
            callback_url = request.build_absolute_uri(reverse("payment_callback"))
            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json",
            }
            data = {
                "email": request.user.email,
                "amount": int(total_amount * 100),
                "reference": deposit.reference,
                "callback_url": callback_url,
                "metadata": {
                    "deposit_id": str(deposit.id),
                },
            }

            response = requests.post(paystack_url, json=data, headers=headers)
            response_data = response.json()

            if response_data["status"]:
                authorization_url = response_data["data"]["authorization_url"]
                return redirect(authorization_url)
            else:
                messages.error(
                    request, "Failed to initialize payment. Please try again."
                )
        return render(request, self.template_name, {"form": form})


@method_decorator(csrf_exempt, name="dispatch")
class PaymentCallbackView(View):
    def get(self, request):
        # Paystack redirects with query parameters
        reference = request.GET.get("reference")
        if not reference:
            messages.error(request, "Invalid payment reference.")
            return redirect("purchase_bundle")

        # Verify the transaction with Paystack
        verify_url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }

        response = requests.get(verify_url, headers=headers)
        response_data = response.json()

        if response_data["status"]:
            data = response_data["data"]
            deposit = Deposit.objects.filter(reference=reference).first()
            if deposit:
                if data["status"] == "success":
                    deposit.status = Deposit.Status.APPROVED
                    deposit.save()
                    messages.success(
                        request,
                        "Payment successful! Your deposit is now approved.",
                    )
                else:
                    deposit.status = Deposit.Status.REJECTED
                    deposit.save()
                    messages.error(request, "Payment was not successful.")
            else:
                messages.error(request, "Deposit not found.")
        else:
            messages.error(request, "Payment verification failed.")

        return redirect("purchase_bundle")


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
                "You created a new ticket for resolution.",
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
                    "You posted a new reply to your ticket.",
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
                    "You updated the status of your ticket.",
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
