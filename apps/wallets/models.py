from decimal import Decimal
import uuid
from django.conf import settings
from django.db import models, transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class Wallet(models.Model):
    """
    Represents a user's wallet, tracking their balance and unique identifier.
    """

    wallet_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Current wallet balance.",
    )
    currency = models.CharField(max_length=50, default="NGN")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.wallet_id)

    def update_balance(self, amount, transaction_type, transaction_id):
        """
        Safely updates the balance and creates an audit log.
        """
        if amount <= 0:
            raise ValueError("Transaction amount must be positive.")

        with transaction.atomic():
            balance_before = self.balance

            # Update the balance using F expression
            self.balance = F("balance") + amount
            self.save(update_fields=["balance", "updated"])

            # Refresh the instance to get the updated balance
            self.refresh_from_db()

            balance_after = self.balance

            # Create audit log
            AuditLog.objects.create(
                wallet=self,
                transaction_type=transaction_type,
                transaction_id=transaction_id,
                amount=amount,
                balance_before=balance_before,
                balance_after=balance_after,
            )


class AuditLog(models.Model):
    """
    Records each change in the wallet's balance for audit purposes.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    wallet = models.ForeignKey(
        "Wallet",
        on_delete=models.PROTECT,
        related_name="audit_logs",
    )
    transaction_type = models.CharField(
        max_length=50,
        help_text="Type of transaction (Deposit, Withdrawal, Purchase, Winning).",
    )
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique ID of the related transaction (Deposit, Purchase, etc.)",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount involved in the transaction.",
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    balance_before = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Wallet balance before the transaction.",
    )
    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Wallet balance after the transaction.",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of the balance change.",
    )

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return (
            f"Audit Log {self.id} for Wallet {self.wallet.id} - {self.transaction_type}"
        )


class Deposit(models.Model):
    """
    Tracks each deposit transaction made to a user's wallet via Paystack.
    """

    class Status(models.TextChoices):
        PENDING = "P", _("Pending")
        COMPLETED = "C", _("Completed")
        FAILED = "F", _("Failed")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet_deposits",
    )
    wallet = models.ForeignKey(
        "Wallet",
        on_delete=models.PROTECT,
        related_name="deposits",
    )
    paystack_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
    )
    amount = models.DecimalField(
        _("Deposit Amount (₦)"),
        max_digits=10,
        decimal_places=2,
        help_text="Amount deposited.",
        validators=[MinValueValidator(Decimal("100.00"))],
    )
    description = models.CharField(
        max_length=255,
        blank=True,
    )
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Status of the deposit transaction.",
    )
    gateway_response = models.CharField(
        max_length=255,
        blank=True,
        help_text="Response from the payment gateway.",
    )
    channel = models.CharField(
        max_length=50,
        blank=True,
        help_text="Payment channel used, e.g., 'card'.",
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address of the customer at the time of transaction.",
    )
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when payment was completed.",
    )
    authorization_code = models.CharField(
        max_length=100,
        blank=True,
        help_text="Authorization code for the payment.",
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-paid_at", "-created"]

    def __str__(self):
        return f"Deposit {self.paystack_id} - {self.amount} for Wallet {self.wallet.id}"


class Withdrawal(models.Model):
    """
    Tracks each withdrawal request made by a user from their wallet balance.
    """

    class Status(models.TextChoices):
        PENDING = "P", _("Pending")
        APPROVED = "A", _("Approved")
        DECLINED = "D", _("Declined")
        CANCELLED = "C", _("Cancelled")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="withdrawals",
        on_delete=models.CASCADE,
    )
    wallet = models.ForeignKey(
        "Wallet",
        related_name="withdrawals",
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Requested withdrawal amount.",
    )
    description = models.TextField(
        _("Description"),
        max_length=300,
        help_text="Withdrawal description.",
    )
    note = models.TextField(
        _("Feedback Note"),
        blank=True,
        null=True,
        help_text="Withdrawal note from Administrator.",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Status of the withdrawal request.",
    )
    processed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date when the withdrawal was processed.",
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Withdrawal {self.id} - {self.status}"


# class Purchase(models.Model):
#     """
#     Tracks each bundle purchase made by a user, including the expected winnings.
#     """

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     wallet = models.ForeignKey(
#         "Wallet", on_delete=models.CASCADE, related_name="purchases"
#     )
#     bundle = models.ForeignKey(
#         Bundle, on_delete=models.CASCADE, related_name="purchases"
#     )
#     price = models.DecimalField(
#         max_digits=10, decimal_places=2, help_text="Purchase price of the bundle."
#     )
#     expected_winning = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         blank=True,
#         null=True,
#         help_text="Expected winning amount based on bundle purchase.",
#     )
#     status = models.CharField(
#         max_length=10,
#         choices=[("PENDING", "Pending"), ("WON", "Won"), ("LOST", "Lost")],
#         default="PENDING",
#         help_text="Purchase status, updated by admin.",
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Purchase {self.id} of Bundle {self.bundle.name} by Wallet {self.wallet.unique_id}"
