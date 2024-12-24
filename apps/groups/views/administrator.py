import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string

from apps.core.utils import create_action, mk_paginator, send_email_thread
from apps.wallets.models import AuditLog

from ..forms import BundleCreateForm, GroupCreateForm, GroupUpdateForm
from ..models import Bundle, Group, GroupRequest, Payout, Purchase

logger = logging.getLogger(__name__)

PAGINATION_COUNT = 20


def is_admin(user):
    """Check if the user has admin privileges."""
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

    template = "groups/administrator/all.html"
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

    template = "groups/administrator/new.html"
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

    template = "groups/administrator/running.html"
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

    template = "groups/administrator/closed.html"
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
    members = mk_paginator(request, members, PAGINATION_COUNT)

    # Fetch pending group requests
    pending_requests = group.group_requests.filter(status=GroupRequest.Status.PENDING)

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

    template = "groups/administrator/detail.html"
    context = {
        "group": group,
        "form": form,
        "members": members,
        "pending_requests": pending_requests,
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def approve_group_request(request, request_id):
    group_request = get_object_or_404(
        GroupRequest, id=request_id, status=GroupRequest.Status.PENDING
    )
    group_request.status = GroupRequest.Status.APPROVED
    group_request.group.bettors.add(group_request.user)
    group_request.save()
    messages.success(
        request, f"Request by {group_request.user.get_full_name()} has been approved."
    )

    # Send approval email
    current_site = get_current_site(request)
    protocol = "https" if request.is_secure() else "http"

    subject = render_to_string(
        "groups/emails/request_approved_subject.txt",
        {"site_name": current_site.name},
    ).strip()

    text_message = render_to_string(
        "groups/emails/request_approved_email.txt",
        {
            "user": group_request.user,
            "group": group_request.group.name,
            "domain": current_site.domain,
            "protocol": protocol,
            "site_name": current_site.name,
        },
    ).strip()

    html_message = render_to_string(
        "groups/emails/request_approved_email.html",
        {
            "user": group_request.user,
            "group": group_request.group.name,
            "domain": current_site.domain,
            "protocol": protocol,
            "site_name": current_site.name,
        },
    )

    send_email_thread(
        subject,
        text_message,
        html_message,
        group_request.user.email,
        group_request.user.get_full_name(),
    )

    return redirect("groups:groups_detail", group_id=group_request.group.group_id)


@login_required
@user_passes_test(is_admin)
def reject_group_request(request, request_id):
    group_request = get_object_or_404(
        GroupRequest, id=request_id, status=GroupRequest.Status.PENDING
    )
    group_request.status = GroupRequest.Status.REJECTED
    group_request.save()
    messages.success(
        request, f"Request by {group_request.user.get_full_name()} has been rejected."
    )

    # Send rejection email
    current_site = get_current_site(request)
    protocol = "https" if request.is_secure() else "http"

    subject = render_to_string(
        "groups/emails/request_rejected_subject.txt",
        {"site_name": current_site.name},
    ).strip()

    text_message = render_to_string(
        "groups/emails/request_rejected_email.txt",
        {
            "user": group_request.user,
            "group": group_request.group.name,
            "domain": current_site.domain,
            "protocol": protocol,
            "site_name": current_site.name,
        },
    ).strip()

    html_message = render_to_string(
        "groups/emails/request_rejected_email.html",
        {
            "user": group_request.user,
            "group": group_request.group.name,
            "domain": current_site.domain,
            "protocol": protocol,
            "site_name": current_site.name,
        },
    )

    send_email_thread(
        subject,
        text_message,
        html_message,
        group_request.user.email,
        group_request.user.get_full_name(),
    )

    return redirect("groups:groups_detail", group_id=group_request.group.group_id)


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
            # Handle Won scenario
            if new_status == Bundle.Status.WON:
                bundle.status = new_status
                bundle.round_outcomes[bundle.current_round] = Bundle.Status.WON
                bundle.round_outcomes = dict(bundle.round_outcomes)
                bundle.save()

                # Process winnings for all participants
                for purchase in bundle.purchases.filter(
                    status=Purchase.Status.APPROVED
                ):
                    potential_win_amount = purchase.payout_amount

                    try:
                        # Credit user wallets
                        wallet = purchase.user.wallet
                        reference = get_random_string(length=12).upper()
                        wallet.update_balance(
                            potential_win_amount,
                            transaction_type=AuditLog.TransactionType.BUNDLE_WINNING,
                            transaction_id=reference,
                        )

                        # Create Payout object
                        Payout.objects.create(
                            user=purchase.user,
                            bundle=bundle,
                            amount=potential_win_amount,
                        )

                        # Send email notification
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

            # Handle Lost scenario
            elif new_status == Bundle.Status.LOST:
                if bundle.current_round < Bundle.MAX_ROUNDS:
                    # Move to the next round
                    bundle.current_round += 1
                    bundle.status = Bundle.Status.PENDING
                    bundle.round_outcomes[bundle.current_round - 1] = Bundle.Status.LOST
                    bundle.save()

                    # Notify participants of the new round
                    for participant in bundle.participants.all():
                        try:
                            email_context = {
                                "user": participant,
                                "bundle": bundle,
                                "next_round": bundle.current_round,
                            }
                            subject = "Update: Bundle Progressing to a New Round"
                            html_content = render_to_string(
                                "accounts/bettor/bundles/email/round.html",
                                email_context,
                            )
                            text_content = render_to_string(
                                "accounts/bettor/bundles/email/round.txt",
                                email_context,
                            )
                            send_email_thread(
                                subject=subject,
                                text_content=text_content,
                                html_content=html_content,
                                recipient_email=participant.email,
                                recipient_name=participant.get_full_name(),
                            )

                            create_action(
                                request.user,
                                "Bundle Status Update",
                                f"Notified {participant} about the bundle moving to the next round.",
                                target=participant.profile,
                            )
                        except Exception as e:
                            logger.error(f"Error sending email to {participant}: {e}")
                            messages.error(
                                request,
                                f"An error occurred while notifying {participant}.",
                            )

                    messages.success(
                        request,
                        f"Bundle marked as Lost and moved to Round {bundle.current_round}. Participants have been notified.",
                    )
                else:
                    # Final round, mark permanently lost
                    bundle.status = Bundle.Status.LOST
                    bundle.round_outcomes[bundle.current_round] = Bundle.Status.LOST
                    bundle.save()

                    # Notify participants of the final loss
                    for purchase in bundle.purchases.filter(
                        status=Purchase.Status.APPROVED
                    ):
                        try:
                            Payout.objects.create(
                                user=purchase.user,
                                bundle=bundle,
                                amount=0,
                                status=Payout.Status.CANCELLED,
                            )

                            email_context = {"user": purchase.user, "bundle": bundle}
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

                    messages.success(
                        request,
                        "Bundle marked as Lost in the final round. No further action can be taken.",
                    )

            return redirect(bundle)
        else:
            messages.error(request, "Invalid status selected.")

    # Get all purchases that are approved for this bundle
    approved_purchases = bundle.purchases.filter(status=Purchase.Status.APPROVED)

    # Update latest outcome for the context
    latest_outcome = (
        Bundle.Status.WON
        if Bundle.Status.WON in bundle.round_outcomes.values()
        else bundle.round_outcomes.get(bundle.current_round, Bundle.Status.PENDING)
    )

    template = "bundles/detail.html"
    context = {
        "bundle": bundle,
        "approved_purchases": approved_purchases,
        "latest_outcome": latest_outcome,
    }

    return render(request, template, context)
