from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from apps.groups.models import Purchase
from apps.accounts.utils import send_email_thread


def payment_successful_email(purchase_id):
    purchase = get_object_or_404(Purchase, purchase_id=purchase_id)

    # Prepare the email content
    subject = "Your Bundle Purchase Has Been Completed"
    text_content = render_to_string(
        "accounts/bettor/bundles/email/acknowledgment.txt",
        {"purchase": purchase},
    )
    html_content = render_to_string(
        "accounts/bettor/bundles/email/acknowledgment.html",
        {"purchase": purchase},
    )

    # Send the email asynchronously using threading
    send_email_thread(
        subject=subject,
        text_content=text_content,
        html_content=html_content,
        recipient_email=purchase.user.email,
        recipient_name=purchase.user.get_full_name(),
    )
