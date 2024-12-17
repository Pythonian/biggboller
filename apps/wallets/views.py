from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import check_password

from apps.accounts.utils import create_action
from apps.wallets.tasks import send_deposit_email, send_withdrawal_email

from .forms import DepositForm, WithdrawalForm, TransactionPINForm
from .models import Deposit, Withdrawal
from .utils import verify_paystack_transaction


@login_required
def wallet_deposit(request):
    """Handles user input for wallet deposits."""
    if not hasattr(request.user, "wallet"):
        messages.error(request, "You need a wallet before making a deposit.")
        return redirect("bettor:dashboard")

    form = DepositForm(request.POST or None)
    if form.is_valid():
        deposit = form.save(commit=False)
        deposit.user = request.user
        deposit.wallet = request.user.wallet
        deposit.reference = get_random_string(length=12).upper()
        deposit.save()

        return redirect("wallet:deposit_pin", reference=deposit.reference)

    template = "accounts/bettor/wallets/deposit.html"
    context = {
        "form": form,
        "wallet_balance": request.user.wallet.balance,
    }
    return render(request, template, context)


@login_required
def wallet_deposit_pin(request, reference):
    """Handles transaction PIN verification for wallet deposits."""
    profile = request.user.profile

    # Retrieve deposit details
    deposit = get_object_or_404(
        Deposit,
        reference=reference,
        user=request.user,
        status=Deposit.Status.PENDING,
    )

    if request.method == "POST":
        form = TransactionPINForm(request.POST)
        if form.is_valid():
            entered_pin = form.cleaned_data["transaction_pin"]

            # Check if the entered PIN matches the stored PIN
            if not check_password(entered_pin, profile.transaction_pin):
                form.add_error("transaction_pin", "Incorrect Transaction PIN.")
            else:
                # Redirect to confirmation page
                return redirect(
                    "wallet:deposit_confirmation",
                    reference=deposit.reference,
                )
    else:
        form = TransactionPINForm()

    template = "accounts/bettor/wallets/deposit_pin.html"
    context = {
        "form": form,
        "deposit": deposit,
    }

    return render(request, template, context)


@login_required
def wallet_deposit_confirmation(request, reference):
    """Displays deposit details for confirmation and handles Paystack popup."""
    deposit = get_object_or_404(
        Deposit,
        reference=reference,
        user=request.user,
        status=Deposit.Status.PENDING,
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

    deposit = get_object_or_404(
        Deposit,
        reference=reference,
        user=request.user,
    )

    if deposit.status == Deposit.Status.COMPLETED:
        messages.warning(request, "Your wallet deposit has already been processed.")
        return redirect("wallet:deposit")

    # Verify the Paystack transaction
    verified, transaction_data = verify_paystack_transaction(reference)

    if not verified:
        messages.error(request, "Payment verification failed. Please try again.")
        return redirect("wallet:deposit")

    # Update deposit and wallet
    deposit.update_deposit_status(transaction_data)
    messages.success(request, "Your deposit was successful!")

    # Sending confirmation email
    send_deposit_email(request, deposit)

    create_action(
        request.user,
        "Wallet Top-up",
        f"has made a wallet deposit of ₦{deposit.amount}.",
        target=request.user.wallet,
    )

    template = "accounts/bettor/wallets/invoice.html"
    context = {
        "deposit": deposit,
    }

    return render(request, template, context)


@login_required
def wallet_withdrawal(request):
    """Handles wallet withdrawal amount and description input."""
    if not hasattr(request.user, "wallet"):
        messages.error(request, "You need a wallet before making a withdrawal.")
        return redirect("bettor:dashboard")

    user_wallet = request.user.wallet

    if request.method == "POST":
        form = WithdrawalForm(
            request.POST,
            wallet_balance=user_wallet.balance,
        )
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            description = form.cleaned_data.get("description", "")

            # Store withdrawal details in the session temporarily
            request.session["withdrawal_data"] = {
                "amount": str(amount),
                "description": description,
            }

            return redirect("wallet:withdrawal_pin")
    else:
        form = WithdrawalForm(wallet_balance=user_wallet.balance)

    template = "accounts/bettor/wallets/withdrawal.html"
    context = {
        "form": form,
        "wallet_balance": user_wallet.balance,
    }

    return render(request, template, context)


@login_required
def wallet_withdrawal_pin(request):
    """Handles transaction PIN verification for wallet withdrawals."""
    profile = request.user.profile

    # Ensure withdrawal data exists in session
    withdrawal_data = request.session.get("withdrawal_data")
    if not withdrawal_data:
        messages.error(request, "Invalid withdrawal request.")
        return redirect("wallet:withdrawal")

    if request.method == "POST":
        form = TransactionPINForm(request.POST)
        if form.is_valid():
            entered_pin = form.cleaned_data["transaction_pin"]

            # Check if the entered PIN matches the stored PIN
            if not check_password(entered_pin, profile.transaction_pin):
                form.add_error("transaction_pin", "Incorrect Transaction PIN.")
            else:
                # Create withdrawal record
                user_wallet = request.user.wallet
                reference = get_random_string(length=12).upper()
                withdrawal = Withdrawal.objects.create(
                    user=request.user,
                    wallet=user_wallet,
                    amount=Decimal(withdrawal_data["amount"]),
                    description=withdrawal_data.get("description", ""),
                    reference=reference,
                )

                # Clear session data
                del request.session["withdrawal_data"]

                # Send email notification
                send_withdrawal_email(request, withdrawal)

                messages.success(
                    request,
                    _(
                        "Your withdrawal request has been submitted and is pending admin review."
                    ),
                )

                create_action(
                    request.user,
                    "Wallet Withdrawal",
                    f"requested a withdrawal of ₦{withdrawal.amount}.",
                    target=user_wallet,
                )

                return redirect("bettor:dashboard")
    else:
        form = TransactionPINForm()

    template = "accounts/bettor/wallets/withdrawal_pin.html"
    context = {
        "form": form,
        "withdrawal_data": withdrawal_data,
    }

    return render(request, template, context)
