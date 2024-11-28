import requests
from django.conf import settings


def verify_paystack_transaction(reference):
    secret_key = settings.PAYSTACK_SECRET_KEY
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {secret_key}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get("data", {})
        if data.get("status") == "success":
            return True, data
    return False, None


def initialize_paystack_transaction(user, amount, reference, callback_url):
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
    response = requests.post(paystack_url, json=data, headers=headers)

    if response.status_code == 200:
        return response.json()["data"]["authorization_url"]
    return None
