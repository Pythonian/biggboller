from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
import logging
from django.contrib.auth import get_user_model

from apps.core.utils import send_email_thread

logger = logging.getLogger(__name__)
User = get_user_model()


def send_deposit_email(request, deposit):
    """Send deposit confirmation email to the user."""
    current_site = get_current_site(request)
    protocol = "https" if request.is_secure() else "http"

    subject = render_to_string(
        "wallets/emails/deposit_subject.txt",
        {"site_name": current_site.name},
    ).strip()

    text_message = render_to_string(
        "wallets/emails/deposit_email.txt",
        {
            "user": deposit.user,
            "deposit": deposit,
            "domain": current_site.domain,
            "protocol": protocol,
            "site_name": current_site.name,
        },
    ).strip()

    html_message = render_to_string(
        "wallets/emails/deposit_email.html",
        {
            "user": deposit.user,
            "deposit": deposit,
            "domain": current_site.domain,
            "protocol": protocol,
            "site_name": current_site.name,
        },
    )

    send_email_thread(
        subject,
        text_message,
        html_message,
        deposit.user.email,
        deposit.user.get_full_name(),
    )


def send_withdrawal_email(request, withdrawal):
    """Send withdrawal request email to the user."""
    current_site = get_current_site(request)
    protocol = "https" if request.is_secure() else "http"

    context = {
        "user": withdrawal.user,
        "amount": withdrawal.amount,
        "description": withdrawal.description,
        "reference": withdrawal.reference,
        "domain": current_site.domain,
        "protocol": protocol,
        "site_name": current_site.name,
    }

    subject = render_to_string(
        "wallets/emails/withdrawal_subject.txt",
        {"site_name": current_site.name},
    ).strip()

    text_message = render_to_string(
        "wallets/emails/withdrawal_email.txt",
        context,
    ).strip()

    html_message = render_to_string(
        "wallets/emails/withdrawal_email.html",
        context,
    )

    send_email_thread(
        subject,
        text_message,
        html_message,
        withdrawal.user.email,
        withdrawal.user.get_full_name(),
    )
