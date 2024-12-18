from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import logging
import threading
from mailjet_rest import Client
from django.conf import settings
import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from apps.accounts.models import Action

logger = logging.getLogger(__name__)


def send_email_via_mailjet(
    subject,
    text_content,
    html_content,
    recipient_email,
    recipient_name=None,
):
    try:
        mailjet = Client(
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            version="v3.1",
        )

        sender = {
            "Email": settings.DEFAULT_FROM_EMAIL,
            "Name": settings.MAILJET_SENDER_NAME,
        }

        recipient = {
            "Email": recipient_email,
            "Name": recipient_name if recipient_name else recipient_email.split("@")[0],
        }

        data = {
            "Messages": [
                {
                    "From": sender,
                    "To": [recipient],
                    "Subject": subject,
                    "TextPart": text_content,
                    "HTMLPart": html_content,
                }
            ]
        }

        result = mailjet.send.create(data=data)
        if result.status_code != 200:
            logger.error(
                f"Failed to send email to {recipient_email}: {result.status_code} {result.json()}"
            )
        else:
            logger.info(
                f"Email sent successfully to {recipient_email}: {result.status_code}"
            )
    except Exception as e:
        logger.exception(
            f"An error occurred while sending email to {recipient_email}: {str(e)}"
        )


def send_email_thread(
    subject,
    text_content,
    html_content,
    recipient_email,
    recipient_name=None,
):
    email_thread = threading.Thread(
        target=send_email_via_mailjet,
        args=(
            subject,
            text_content,
            html_content,
            recipient_email,
            recipient_name,
        ),
    )
    email_thread.start()


def create_action(user, title, verb, target=None):
    # check for any similar action made in the last minute
    now = timezone.now()
    last_minute = now - datetime.timedelta(seconds=60)
    similar_actions = Action.objects.filter(
        user_id=user.id,
        title=title,
        verb=verb,
        created__gte=last_minute,
    )
    if target:
        target_ct = ContentType.objects.get_for_model(target)
        similar_actions = similar_actions.filter(
            target_ct=target_ct,
            target_id=target.id,
        )
    if not similar_actions:
        # no existing actions found
        action = Action(user=user, title=title, verb=verb, target=target)
        action.save()
        return True
    return False


def mk_paginator(request, items, num_items):
    """
    Function to paginate querysets.

    :param request: The current request object
    :param items: The queryset to be paginated
    :param num_items: The number of items to be displayed per page
    :return: A paginated queryset
    """
    paginator = Paginator(items, num_items)
    page = request.GET.get("page", 1)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, return the first page.
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range, return the last page of results.
        items = paginator.page(paginator.num_pages)
    return items
