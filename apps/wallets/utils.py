"""Utility functions for handling payments with Paystack API."""

import logging
import requests

from django.conf import settings

logger = logging.getLogger(__name__)


def verify_paystack_transaction(reference):
    """Verify a Paystack transaction using the reference."""
    secret_key = settings.PAYSTACK_SECRET_KEY
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {secret_key}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json().get("data", {})
        if data.get("status") == "success":
            return True, data
    except requests.RequestException as e:
        logger.error(f"Error verifying Paystack transaction: {e}")
    except ValueError as e:
        logger.error(f"Error decoding JSON response: {e}")

    return False, None


def initialize_paystack_transaction(user, amount, reference, callback_url):
    """Initialize a Paystack transaction."""
    paystack_url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": user.email,
        "amount": int(amount * 100),
        "reference": reference,
        "callback_url": callback_url,
    }

    try:
        response = requests.post(paystack_url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()["data"]["authorization_url"]
    except requests.RequestException as e:
        logger.error(f"Error initializing Paystack transaction: {e}")
    except ValueError as e:
        logger.error(f"Error decoding JSON response: {e}")

    return None
