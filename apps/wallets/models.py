from decimal import Decimal
import uuid
from django.conf import settings
from django.db import models, transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from django.core.validators import (
    MinValueValidator,
    MinLengthValidator,
    MaxLengthValidator,
)


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Wallet(TimeStampedModel):
    """Represents a user's wallet, tracking their balance."""

    wallet_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
        verbose_name=_("User"),
    )
    balance = models.DecimalField(
        _("Balance"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=_("Current wallet balance."),
    )

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Wallet")
        verbose_name_plural = _("Wallets")

    def __str__(self) -> str:
        return f"Wallet: {self.user.get_full_name()}"

    def update_balance(
        self,
        amount: Decimal,
        transaction_type: str,
        transaction_id: str,
    ) -> None:
        """
        Safely updates the wallet balance and logs the transaction.

        Args:
            amount (Decimal): The amount to update the balance by.
            transaction_type (str): Type of the transaction.
            transaction_id (str): Unique identifier for the transaction.
        """
        if amount <= Decimal("0.00"):
            raise ValueError("Transaction amount must be positive.")

        with transaction.atomic():
            fields_to_update = ["balance", "updated"]
            balance_before = self.balance

            Wallet.objects.filter(pk=self.pk).update(balance=F("balance") + amount)
            # Ensure latest value is fetched.
            self.refresh_from_db(fields=fields_to_update)

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


class AuditLog(TimeStampedModel):
    """Records each change in the wallet's balance for audit purposes."""

    class TransactionType(models.TextChoices):
        WALLET_CREATION = "WC", _("Wallet Creation")
        WALLET_DEPOSIT = "WD", _("Wallet Deposit")
        WALLET_WITHDRAWAL = "WW", _("Wallet Withdrawal")
        BUNDLE_PURCHASE = "BP", _("Bundle Purchase")
        BUNDLE_WINNING = "BW", _("Bundle Winning")

    audit_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    wallet = models.ForeignKey(
        "Wallet",
        on_delete=models.PROTECT,
        related_name="audit_logs",
        verbose_name=_("Wallet"),
    )
    transaction_type = models.CharField(
        _("Transaction Type"),
        max_length=2,
        choices=TransactionType.choices,
        help_text=_("Type of transaction."),
    )
    transaction_id = models.CharField(
        _("Transaction ID"),
        max_length=20,
        help_text=_("Unique ID of the related transaction."),
    )
    amount = models.DecimalField(
        _("Amount"),
        max_digits=12,
        decimal_places=2,
        help_text=_("Amount involved in the transaction."),
    )
    balance_before = models.DecimalField(
        _("Balance Before"),
        max_digits=12,
        decimal_places=2,
        help_text=_("Wallet balance before the transaction."),
    )
    balance_after = models.DecimalField(
        _("Balance After"),
        max_digits=12,
        decimal_places=2,
        help_text=_("Wallet balance after the transaction."),
    )

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Audit Log")
        verbose_name_plural = _("Audit Logs")

    def __str__(self):
        return f"Audit Log: {self.get_transaction_type_display()} - Amount: {self.amount} ({self.created})"


class Deposit(TimeStampedModel):
    """Tracks each deposit transaction made to a user's wallet."""

    class Status(models.TextChoices):
        PENDING = "P", _("Pending")
        COMPLETED = "C", _("Completed")
        FAILED = "F", _("Failed")

    deposit_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet_deposits",
        verbose_name=_("User"),
    )
    wallet = models.ForeignKey(
        "Wallet",
        on_delete=models.PROTECT,
        related_name="deposits",
        verbose_name=_("Wallet"),
    )
    reference = models.CharField(
        _("Reference"),
        max_length=20,
        unique=True,
    )
    amount = models.DecimalField(
        _("Deposit Amount (₦)"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Amount deposited."),
        validators=[MinValueValidator(Decimal("1000.00"))],
    )
    description = models.CharField(
        _("Description"),
        max_length=50,
        blank=True,
        default="",
        validators=[MinLengthValidator(5), MaxLengthValidator(50)],
        help_text=_("Description of the Wallet Deposit"),
    )
    status = models.CharField(
        _("Status"),
        max_length=1,
        choices=Status.choices,
        default=Status.PENDING,
        help_text=_("Status of the deposit transaction."),
    )
    gateway_response = models.CharField(
        _("Gateway Response"),
        max_length=255,
        default="",
        help_text=_("Response from the payment gateway."),
    )
    channel = models.CharField(
        _("Payment Channel"),
        max_length=50,
        default="",
        help_text=_("Payment channel used, e.g., 'card'."),
    )
    ip_address = models.GenericIPAddressField(
        _("IP Address"),
        blank=True,
        null=True,
        help_text=_("IP address of the customer at the time of transaction."),
    )
    paid_at = models.DateTimeField(
        _("Paid At"),
        blank=True,
        null=True,
        help_text=_("Timestamp when payment was completed."),
    )
    authorization_code = models.CharField(
        _("Authorization Code"),
        max_length=100,
        default="",
        help_text=_("Authorization code for the payment."),
    )

    class Meta:
        ordering = ["-paid_at", "-created"]

    def __str__(self):
        return (
            f"Deposit #{self.reference} - ₦{self.amount} for Wallet {self.wallet.user}"
        )

    def update_deposit_status(self, transaction_data):
        """Update deposit status and wallet balance."""
        self.status = Deposit.Status.COMPLETED
        self.gateway_response = transaction_data.get("gateway_response", "")
        self.channel = transaction_data.get("channel", "")
        self.ip_address = transaction_data.get("ip_address", "")
        self.paid_at = transaction_data.get("paid_at", "")
        self.authorization_code = transaction_data.get("authorization", {}).get(
            "authorization_code", ""
        )
        self.save()

        # Update wallet balance
        self.wallet.update_balance(
            amount=self.amount,
            transaction_type=AuditLog.TransactionType.WALLET_DEPOSIT,
            transaction_id=self.reference,
        )


class Withdrawal(TimeStampedModel):
    """Tracks each withdrawal request made by a user from their wallet balance."""

    class Status(models.TextChoices):
        PENDING = "P", _("Pending")
        APPROVED = "A", _("Approved")
        DECLINED = "D", _("Declined")
        CANCELLED = "C", _("Cancelled")

    withdrawal_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text=_("Unique identifier for the withdrawal."),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="withdrawals",
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        help_text=_("User initiating the withdrawal."),
    )
    wallet = models.ForeignKey(
        "Wallet",
        related_name="withdrawals",
        on_delete=models.PROTECT,
        verbose_name=_("Wallet"),
        help_text=_("Wallet associated with this withdrawal."),
    )
    amount = models.DecimalField(
        _("Withdrawal Amount (₦)"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Requested withdrawal amount."),
    )
    description = models.CharField(
        _("Description"),
        max_length=50,
        validators=[MinLengthValidator(5), MaxLengthValidator(50)],
        help_text=_("Description of the withdrawal request."),
    )
    note = models.TextField(
        _("Feedback Note"),
        blank=True,
        help_text=_("Administrator's feedback or reason for status change."),
    )
    reference = models.CharField(
        _("Reference"),
        max_length=20,
        unique=True,
        help_text=_("Unique reference number for this withdrawal."),
    )
    status = models.CharField(
        _("Status"),
        max_length=1,
        choices=Status.choices,
        default=Status.PENDING,
        help_text=_("Current status of the withdrawal request."),
    )
    processed_at = models.DateTimeField(
        _("Processed At"),
        blank=True,
        null=True,
        help_text=_("Date and time the withdrawal was processed."),
    )

    class Meta:
        ordering = ["-processed_at", "-created"]
        verbose_name = _("Withdrawal")
        verbose_name_plural = _("Withdrawals")

    def __str__(self):
        return f"Withdrawal {self.reference} - ₦{self.amount} ({self.get_status_display()})"
