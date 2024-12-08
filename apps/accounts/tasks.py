from celery import shared_task
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.template.loader import render_to_string

from apps.groups.models import Purchase
from apps.accounts.utils import send_email_thread


@shared_task
def send_otp_email(email, otp):
    subject = "Your OTP for Bundle Purchase"
    message = f"Your OTP is {otp}. It is valid for the next 10 minutes."
    html_message = f"""
    <html>
        <body>
            <p>Dear User,</p>
            <p>Your OTP for bundle purchase is <strong>{otp}</strong>. It is valid for the next 10 minutes.</p>
            <p>Thank you for using our platform!</p>
        </body>
    </html>
    """
    send_mail(
        subject, message, "support@yourdomain.com", [email], html_message=html_message
    )


@shared_task
def send_success_email(email, amount, balance):
    subject = "Payment Successful"
    message = f"Your payment of ₦{amount} was successful. Your new wallet balance is ₦{balance}."
    html_message = f"""
    <html>
        <body>
            <p>Dear User,</p>
            <p>Your payment of <strong>₦{amount}</strong> was successful.</p>
            <p>Your new wallet balance is <strong>₦{balance}</strong>.</p>
            <p>Thank you for using our platform!</p>
        </body>
    </html>
    """
    send_mail(
        subject, message, "support@yourdomain.com", [email], html_message=html_message
    )


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
