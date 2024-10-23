# from celery import shared_task
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.template.loader import render_to_string

from apps.accounts.models import Deposit
from apps.accounts.utils import send_email_thread


# @shared_task
# def payment_successful_email(deposit_id):
#     deposit = get_object_or_404(Deposit, id=deposit_id)
#     mail_sent = send_mail(
#         subject="Thank you for your contribution on When Will I Be Famous?",
#         message=render_to_string("acknowledgment.txt", {"deposit": deposit}),
#         from_email=settings.AUTHOR_EMAIL,
#         recipient_list=[deposit.user.email],
#         fail_silently=False,
#         html_message=render_to_string(
#             "acknowledgment.html",
#             {"deposit": deposit},
#         ),
#     )
#     return mail_sent


def payment_successful_email(deposit_id):
    deposit = get_object_or_404(Deposit, id=deposit_id)

    # Prepare the email content
    subject = "Your Bundle Purchase Has Been Completed"
    text_content = render_to_string(
        "accounts/bettor/bundles/email/acknowledgment.txt",
        {"deposit": deposit},
    )
    html_content = render_to_string(
        "accounts/bettor/bundles/email/acknowledgment.html",
        {"deposit": deposit},
    )

    # Send the email asynchronously using threading
    send_email_thread(
        subject=subject,
        text_content=text_content,
        html_content=html_content,
        recipient_email=deposit.user.email,
        recipient_name=deposit.user.get_full_name(),
    )


# def payment_successful_email(deposit_id):
#     deposit = get_object_or_404(Deposit, id=deposit_id)

#     # Prepare the email content
#     subject = "Thank you for your contribution on When Will I Be Famous?"

#     # Render the email contents
#     text_content = render_to_string(
#         "accounts/bettor/bundles/email/acknowledgment.txt",
#         {"deposit": deposit},
#     )
#     html_content = render_to_string(
#         "accounts/bettor/bundles/email/acknowledgment.html",
#         {"deposit": deposit},
#     )

#     # Log for debugging
#     if not text_content and not html_content:
#         logger.error(f"Email content is empty for deposit ID: {deposit_id}")
#         return

#     # Send the email asynchronously using threading
#     send_email_thread(
#         subject=subject,
#         text_content=text_content,
#         html_content=html_content,
#         recipient_email=deposit.user.email,
#         recipient_name=deposit.user.get_full_name(),
#     )
