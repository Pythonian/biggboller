import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone

from apps.core.utils import mk_paginator, create_action

from .models import Ticket
from .forms import TicketCreateForm, TicketReplyForm


logger = logging.getLogger(__name__)

PAGINATION_COUNT = 20


def is_admin(user):
    """
    Check if the user has admin privileges.
    Adjust this function based on your authentication setup.
    """
    return user.is_staff or user.is_superuser


################
# ADMIN TICKETS
################


@login_required
@user_passes_test(is_admin)
def admin_tickets_all(request):
    tickets = Ticket.objects.all()
    total_tickets = tickets.count()
    pending_tickets = tickets.filter(status=Ticket.Status.PENDING).count()
    answered_tickets = tickets.filter(status=Ticket.Status.ANSWERED).count()
    closed_tickets = tickets.filter(status=Ticket.Status.CLOSED).count()

    tickets = mk_paginator(request, tickets, PAGINATION_COUNT)

    template = "tickets/administrator/all.html"
    context = {
        "tickets": tickets,
        "total_tickets": total_tickets,
        "pending_tickets": pending_tickets,
        "answered_tickets": answered_tickets,
        "closed_tickets": closed_tickets,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_tickets_detail(request, ticket_id):
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
                # TODO: Send an email to the Bettor whenever an Admin replies
                # to the Ticket
                return redirect(
                    "ticket:admin_tickets_detail", ticket_id=ticket.ticket_id
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
            else:
                messages.error(request, "Invalid status selected.")
            # TODO: Send an email to the Bettor when an Admin updates the
            # status of the Ticket.
            return redirect(
                "ticket:admin_tickets_detail",
                ticket_id=ticket.ticket_id,
            )

    else:
        reply_form = TicketReplyForm()

    template = "tickets/administrator/detail.html"
    context = {
        "ticket": ticket,
        "replies": replies,
        "reply_form": reply_form,
    }
    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_tickets_pending(request):
    tickets = Ticket.objects.pending()
    pending_tickets = tickets.filter(status=Ticket.Status.PENDING).count()

    tickets = mk_paginator(request, tickets, PAGINATION_COUNT)

    template = "tickets/administrator/pending.html"
    context = {
        "tickets": tickets,
        "pending_tickets": pending_tickets,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_tickets_answered(request):
    tickets = Ticket.objects.answered()
    answered_tickets = tickets.filter(status=Ticket.Status.ANSWERED).count()

    template = "tickets/administrator/answered.html"
    context = {
        "tickets": tickets,
        "answered_tickets": answered_tickets,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def admin_tickets_closed(request):
    tickets = Ticket.objects.closed()
    closed_tickets = tickets.filter(status=Ticket.Status.CLOSED).count()

    tickets = mk_paginator(request, tickets, PAGINATION_COUNT)

    template = "tickets/administrator/closed.html"
    context = {
        "tickets": tickets,
        "closed_tickets": closed_tickets,
    }

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

    tickets = mk_paginator(request, tickets, PAGINATION_COUNT)

    template = "tickets/bettor/all.html"
    context = {
        "tickets": tickets,
        "total_tickets": total_tickets,
        "pending_tickets": pending_tickets,
        "answered_tickets": answered_tickets,
        "closed_tickets": closed_tickets,
    }

    return render(request, template, context)


@login_required
def bettor_tickets_create(request):
    if request.method == "POST":
        form = TicketCreateForm(request.POST)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.status = Ticket.Status.PENDING
            ticket.user = request.user
            ticket.save()

            messages.success(
                request,
                f'Your Ticket with ID "#{ticket.ticket_id}" has been created successfully.',
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

    template = "tickets/bettor/create.html"
    context = {
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
                    "ticket:bettor_tickets_detail",
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
                "ticket:bettor_tickets_detail",
                ticket_id=ticket.ticket_id,
            )

    else:
        reply_form = TicketReplyForm()

    template = "tickets/bettor/detail.html"
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

    template = "tickets/bettor/pending.html"
    context = {
        "tickets": tickets,
        "pending_tickets": pending_tickets,
    }

    return render(request, template, context)


@login_required
def bettor_tickets_answered(request):
    tickets = Ticket.objects.answered().filter(user=request.user)
    answered_tickets = tickets.filter(status=Ticket.Status.ANSWERED).count()

    template = "tickets/bettor/answered.html"
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

    template = "tickets/bettor/closed.html"
    context = {
        "tickets": tickets,
        "closed_tickets": closed_tickets,
    }

    return render(request, template, context)
