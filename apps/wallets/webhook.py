import json
import logging
import hmac
import hashlib
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import Deposit
from .tasks import send_deposit_confirmation_email

logger = logging.getLogger(__name__)


@csrf_exempt
def paystack_webhook(request):
    # Verify webhook signature
    paystack_signature = request.headers.get("X-Paystack-Signature")
    computed_signature = hmac.new(
        key=settings.PAYSTACK_WEBHOOK_SECRET.encode(),
        msg=request.body,
        digestmod=hashlib.sha512,
    ).hexdigest()

    if computed_signature != paystack_signature:
        logger.warning("Webhook signature verification failed.")
        return HttpResponse("Invalid signature", status=403)

    # Parse payload and validate event
    try:
        payload = json.loads(request.body)
        event = payload.get("event")
        if not event:
            return HttpResponse("Event type missing", status=400)
    except json.JSONDecodeError:
        logger.error("Invalid JSON payload")
        return HttpResponse("Invalid JSON", status=400)

    if event == "charge.success":
        data = payload.get("data", {})
        reference = data.get("reference")
        amount = data.get("amount") / 100
        gateway_response = data.get("gateway_response")
        channel = data.get("channel")
        ip_address = data.get("ip_address")
        paid_at = data.get("paid_at")
        authorization_code = data.get("authorization", {}).get("authorization_code")

        try:
            deposit = Deposit.objects.get(
                transaction_id=reference,
                status=Deposit.Status.PENDING,
            )
        except Deposit.DoesNotExist:
            logger.error(
                f"Deposit with reference {reference} not found or already processed."
            )
            return HttpResponse(
                "Deposit not found or already processed.",
                status=404,
            )

        deposit.status = Deposit.Status.APPROVED
        deposit.gateway_response = gateway_response
        deposit.channel = channel
        deposit.ip_address = ip_address
        deposit.paid_at = timezone.datetime.fromisoformat(
            paid_at.replace("Z", "+00:00")
        )
        deposit.authorization_code = authorization_code
        deposit.save()

        deposit.wallet.update_balance(
            amount=amount,
            transaction_type="Deposit Approved",
            transaction_id=deposit.transaction_id,
        )

        send_deposit_confirmation_email.delay(deposit.user.id, deposit.amount)

        return HttpResponse(status=200)

    return HttpResponse("Unhandled event", status=200)
