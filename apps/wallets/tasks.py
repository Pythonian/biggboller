from celery import shared_task
from mailjet_rest import Client
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
import logging
from django.contrib.auth import get_user_model

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
