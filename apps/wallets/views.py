from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string

from apps.accounts.utils import send_email_thread

from .forms import DepositForm
from .models import Deposit
from .utils import verify_paystack_transaction


@login_required
def wallet_deposit(request):
    """Handles user input for wallet deposits."""
    if not hasattr(request.user, "wallet"):
        messages.error(request, "You need a wallet before making a deposit.")
        return redirect("bettor:dashboard")

    if request.method == "POST":
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            description = form.cleaned_data.get("description", "")
            paystack_ref = get_random_string(length=12).upper()

            # Create the deposit record
            deposit = Deposit.objects.create(
                user=request.user,
                wallet=request.user.wallet,
                amount=amount,
                description=description,
                paystack_id=paystack_ref,
                status=Deposit.Status.PENDING,
            )

            # Save deposit ID in session and redirect to confirmation
            request.session["transaction_id"] = str(deposit.id)
            return redirect("wallet:confirmation")
    else:
        form = DepositForm()

    return render(request, "accounts/bettor/wallets/deposit.html", {"form": form})


@login_required
def wallet_deposit_confirmation(request):
    """Displays deposit details for confirmation and handles Paystack popup."""
    transaction_id = request.session.get("transaction_id")

    if not transaction_id:
        messages.error(request, "No deposit transaction found.")
        return redirect("wallet:deposit")

    deposit = get_object_or_404(Deposit, id=transaction_id, user=request.user)

    context = {
        "deposit": deposit,
        "paystack_key": settings.PAYSTACK_PUBLIC_KEY,
        "email": request.user.email,
        "amount": int(deposit.amount * 100),
    }
    return render(request, "accounts/bettor/wallets/deposit_confirmation.html", context)


@login_required
def wallet_invoice(request):
    """Handles Paystack payment verification and updates wallet balance."""
    reference = request.GET.get("reference")

    if not reference:
        messages.error(request, "Invalid transaction reference.")
        return redirect("wallet:deposit")

    deposit = get_object_or_404(Deposit, paystack_id=reference)

    if deposit.status == Deposit.Status.COMPLETED:
        messages.warning(request, "Your wallet deposit has already been processed.")
        return redirect("bettor:dashboard")

    # Verify the Paystack transaction
    verified, transaction_data = verify_paystack_transaction(reference)

    if not verified:
        messages.error(request, "Payment verification failed. Please try again.")
        return redirect("wallet:deposit")

    # Update deposit record and wallet balance
    deposit.status = Deposit.Status.COMPLETED
    deposit.gateway_response = transaction_data.get("gateway_response", "")
    deposit.channel = transaction_data.get("channel", "")
    deposit.ip_address = transaction_data.get("ip_address", "")
    deposit.paid_at = transaction_data.get("paid_at", "")
    deposit.authorization_code = transaction_data.get("authorization", {}).get(
        "authorization_code", ""
    )
    deposit.save()

    deposit.wallet.update_balance(
        amount=deposit.amount,
        transaction_type="Deposit Completed",
        transaction_id=deposit.id,
    )

    # Send confirmation email
    subject = "Bigg-Boller Wallet Deposit Confirmation"
    html_content = render_to_string(
        "wallets/deposit_confirmation_email.html",
        {"user": request.user, "deposit": deposit},
    )
    text_content = f"Hi {request.user.first_name},\n\nYour wallet deposit of ₦{deposit.amount} was successful. Your wallet balance has been updated."

    send_email_thread(
        subject=subject,
        text_content=text_content,
        html_content=html_content,
        recipient_email=request.user.email,
        recipient_name=request.user.get_full_name(),
    )

    messages.success(request, "Your deposit was successful!")

    template = "accounts/bettor/wallets/invoice.html"
    context = {"deposit": deposit}

    return render(request, template, context)


@login_required
def wallet_withdrawal(request):
    pass


@login_required
def wallet_transaction(request):
    pass
