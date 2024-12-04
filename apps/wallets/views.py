from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string

from apps.accounts.utils import send_email_thread, create_action

from .forms import DepositForm, WithdrawalForm
from .models import Deposit, Withdrawal
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
            _ = Deposit.objects.create(
                user=request.user,
                wallet=request.user.wallet,
                amount=amount,
                description=description,
                paystack_id=paystack_ref,
                status=Deposit.Status.PENDING,
            )

            # Save deposit ID in session and redirect to confirmation
            request.session["transaction_id"] = paystack_ref
            return redirect("wallet:confirmation")
        else:
            messages.warning(
                request,
                "An error occured during form submission.",
            )
    else:
        form = DepositForm()

    template = "accounts/bettor/wallets/deposit.html"
    context = {
        "form": form,
        "wallet_balance": request.user.wallet.balance,
    }

    return render(request, template, context)


@login_required
def wallet_deposit_confirmation(request):
    """Displays deposit details for confirmation and handles Paystack popup."""
    transaction_id = request.session.get("transaction_id")

    if not transaction_id:
        messages.error(request, "No deposit transaction found.")
        return redirect("wallet:deposit")

    deposit = get_object_or_404(
        Deposit,
        paystack_id=transaction_id,
        user=request.user,
    )

    template = "accounts/bettor/wallets/deposit_confirmation.html"
    context = {
        "deposit": deposit,
        "paystack_key": settings.PAYSTACK_PUBLIC_KEY,
        "email": request.user.email,
        "amount": int(deposit.amount * 100),
    }
    return render(request, template, context)


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

    messages.success(request, "Your deposit was successful!")

    # Sending confirmation email
    current_site = get_current_site(request)
    protocol = "https" if request.is_secure() else "http"

    subject = render_to_string(
        "wallets/emails/deposit_subject.txt",
        {"site_name": current_site.name},
    ).strip()

    text_message = render_to_string(
        "wallets/emails/deposit_email.txt",
        {
            "user": request.user,
            "deposit": deposit,
            "domain": current_site.domain,
            "protocol": protocol,
            "site_name": current_site.name,
        },
    ).strip()

    html_message = render_to_string(
        "wallets/emails/deposit_email.html",
        {
            "user": request.user,
            "deposit": deposit,
            "domain": current_site.domain,
            "protocol": protocol,
            "site_name": current_site.name,
        },
    )

    send_email_thread(
        subject,
        text_message,
        html_message,
        request.user.email,
        request.user.get_full_name(),
    )

    create_action(
        request.user,
        "Wallet Top-up",
        f"has made a wallet deposit of #{deposit.amount}.",
        target=request.user.wallet,
    )

    template = "accounts/bettor/wallets/invoice.html"
    context = {
        "deposit": deposit,
    }

    return render(request, template, context)


@login_required
def wallet_withdrawal(request):
    """Handles wallet withdrawal requests."""
    wallet_balance = request.user.wallet.balance

    if not hasattr(request.user, "wallet"):
        messages.error(request, "You need a wallet before making a withdrawal.")
        return redirect("bettor:dashboard")

    if request.method == "POST":
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            description = form.cleaned_data.get("description", "")

            # Check wallet balance
            if amount > request.user.wallet.balance:
                messages.error(
                    request,
                    "Insufficient balance for this withdrawal request. Please try again.",
                )
                return redirect("bettor:dashboard")

            # Create withdrawal record
            _ = Withdrawal.objects.create(
                user=request.user,
                wallet=request.user.wallet,
                amount=amount,
                description=description,
                status=Withdrawal.Status.PENDING,
            )

            messages.success(
                request,
                "Your withdrawal request has been submitted and is pending admin review.",
            )

            create_action(
                request.user,
                "Wallet Withdrawal",
                f"has made a wallet withdrawal request of #{amount}.",
                target=request.user.wallet,
            )

            return redirect("bettor:dashboard")
    else:
        form = WithdrawalForm()

    template = "accounts/bettor/wallets/withdrawal.html"
    context = {
        "form": form,
        "wallet_balance": wallet_balance,
    }

    return render(request, template, context)


@login_required
def wallet_transaction(request):
    pass
