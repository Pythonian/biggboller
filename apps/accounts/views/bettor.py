from django.contrib.auth.decorators import login_required
import uuid
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from apps.accounts.forms import BundlePurchaseForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from apps.accounts.models import Bundle, Deposit, Action
from apps.core.utils import mk_paginator

PAGINATION_COUNT = 10


@login_required
def bettor_dashboard(request):
    template = "accounts/bettor/dashboard.html"
    context = {}

    return render(request, template, context)


@login_required
def bettor_profile(request):
    bettor = request.user
    actions = Action.objects.filter(user=bettor)

    template = "accounts/bettor/profile.html"
    context = {
        "bettor": bettor,
        "actions": actions,
    }

    return render(request, template, context)


@login_required
def bettor_settings(request):
    bettor = request.user

    template = "accounts/bettor/settings.html"
    context = {
        "bettor": bettor,
    }

    return render(request, template, context)


def bettor_bundles_all(request):
    bundles = Bundle.objects.all()
    pending_bundles = bundles.filter(status=Bundle.Status.PENDING).count()

    bundles = mk_paginator(request, bundles, PAGINATION_COUNT)

    template = "accounts/bettor/bundles/all.html"
    context = {
        "bundles": bundles,
        "pending_bundles": pending_bundles,
    }

    return render(request, template, context)


class PurchaseBundleView(View):
    template_name = "accounts/bettor/purchase_bundle.html"

    def get(self, request):
        form = BundlePurchaseForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = BundlePurchaseForm(request.POST)
        if form.is_valid():
            bundle = form.cleaned_data["bundle"]
            quantity = form.cleaned_data["quantity"]
            total_amount = bundle.price * quantity

            # Generate a unique reference
            reference = f"DEP-{uuid.uuid4().hex[:10].upper()}"

            # Create a Deposit instance
            deposit = Deposit.objects.create(
                user=request.user,
                bundle=bundle,
                quantity=quantity,
                amount=total_amount,
                reference=reference,
                status=Deposit.Status.PENDING,
            )

            # Initialize Paystack payment
            paystack_url = "https://api.paystack.co/transaction/initialize"
            callback_url = request.build_absolute_uri(reverse("payment_callback"))
            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json",
            }
            data = {
                "email": request.user.email,
                "amount": int(total_amount * 100),
                "reference": deposit.reference,
                "callback_url": callback_url,
                "metadata": {
                    "deposit_id": str(deposit.id),
                },
            }

            response = requests.post(paystack_url, json=data, headers=headers)
            response_data = response.json()

            if response_data["status"]:
                authorization_url = response_data["data"]["authorization_url"]
                return redirect(authorization_url)
            else:
                messages.error(
                    request, "Failed to initialize payment. Please try again."
                )
        return render(request, self.template_name, {"form": form})


@method_decorator(csrf_exempt, name="dispatch")
class PaymentCallbackView(View):
    def get(self, request):
        # Paystack redirects with query parameters
        reference = request.GET.get("reference")
        if not reference:
            messages.error(request, "Invalid payment reference.")
            return redirect("purchase_bundle")

        # Verify the transaction with Paystack
        verify_url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }

        response = requests.get(verify_url, headers=headers)
        response_data = response.json()

        if response_data["status"]:
            data = response_data["data"]
            deposit = Deposit.objects.filter(reference=reference).first()
            if deposit:
                if data["status"] == "success":
                    deposit.status = Deposit.Status.APPROVED
                    deposit.save()
                    messages.success(
                        request,
                        "Payment successful! Your deposit is now approved.",
                    )
                else:
                    deposit.status = Deposit.Status.REJECTED
                    deposit.save()
                    messages.error(request, "Payment was not successful.")
            else:
                messages.error(request, "Deposit not found.")
        else:
            messages.error(request, "Payment verification failed.")

        return redirect("purchase_bundle")


class GetBundlePriceView(View):
    def get(self, request):
        bundle_id = request.GET.get("bundle_id")
        try:
            bundle = Bundle.objects.get(id=bundle_id)
            return JsonResponse({"price": float(bundle.price)})
        except Bundle.DoesNotExist:
            return JsonResponse({"error": "Bundle not found"}, status=404)
