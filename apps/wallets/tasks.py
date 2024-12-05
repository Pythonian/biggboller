from celery import shared_task
from mailjet_rest import Client
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
import logging
from django.contrib.auth import get_user_model

from apps.accounts.utils import send_email_thread

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def send_deposit_confirmation_email(user_id, amount):
    user = User.objects.get(id=user_id)
    subject = "Your Deposit is Complete"

    site_name = Site.objects.get_current().name

    context = {
        "user": user,
        "amount": amount,
        "site_name": site_name,
    }
    text_content = f"Dear {user.get_full_name()},\n\nYour deposit of ₦{amount} has been successfully completed and added to your wallet."
    html_content = render_to_string("emails/deposit_confirmation_email.html", context)

    try:
        mailjet = Client(
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY), version="v3.1"
        )

        data = {
            "Messages": [
                {
                    "From": {
                        "Email": settings.DEFAULT_FROM_EMAIL,
                        "Name": settings.MAILJET_SENDER_NAME,
                    },
                    "To": [
                        {
                            "Email": user.email,
                            "Name": user.get_full_name(),
                        }
                    ],
                    "Subject": subject,
                    "TextPart": text_content,
                    "HTMLPart": html_content,
                }
            ]
        }

        result = mailjet.send.create(data=data)
        if result.status_code != 200:
            logger.error(
                f"Failed to send email to {user.email}: {result.status_code} {result.json()}"
            )
        else:
            logger.info(f"Deposit confirmation email sent to {user.email}")

    except Exception as e:
        logger.exception(
            f"An error occurred while sending email to {user_id}: {str(e)}"
        )


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
