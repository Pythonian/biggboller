import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Deposit(models.Model):
    """
    Represents a payment (stake) made by a bettor for a bundle.
    """

    class Status(models.TextChoices):
        PENDING = "P", _("Pending")
        APPROVED = "A", _("Approved")
        CANCELLED = "C", _("Cancelled")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    # deposit_id = models.UUIDField(
    #     default=uuid.uuid4,
    #     editable=False,
    #     unique=True,
    # )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deposits",
        verbose_name=_("User"),
    )
    bundle = models.ForeignKey(
        "Bundle",
        on_delete=models.CASCADE,
        related_name="deposits",
        verbose_name=_("Bundle"),
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_("Quantity"),
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Amount"),
    )
    payout_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Payout Amount"),
    )
    # transaction_id = models.CharField(
    #     max_length=20,
    #     unique=True,
    #     help_text="Unique ID of the related transaction (Deposit, Purchase, etc.)",
    # )
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Status"),
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Deposit")
        verbose_name_plural = _("Deposits")
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user} - {self.bundle.name} - {self.amount}"

    @property
    def potential_win(self):
        """
        Calculate the user's potential win based on the amount they
        paid and the bundle's winning percentage.
        """
        return self.amount * (self.bundle.winning_percentage / 100)

    @property
    def is_purchase_complete(self):
        return self.status == self.Status.APPROVED


class Payout(models.Model):
    """
    Represents a payout for a bettor after a bundle is won.
    """

    class Status(models.TextChoices):
        PENDING = "P", _("Pending")
        APPROVED = "A", _("Approved")
        CANCELLED = "C", _("Cancelled")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payouts",
        verbose_name=_("User"),
    )
    bundle = models.ForeignKey(
        "Bundle",
        on_delete=models.CASCADE,
        related_name="payouts",
        verbose_name=_("Bundle"),
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Amount"),
        help_text=_("The amount the bettor will be paid."),
    )
    note = models.TextField(
        verbose_name=_("Payout Note"),
        help_text=_("A note by the admin."),
    )
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Status"),
    )
    paid_on = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Payout")
        verbose_name_plural = _("Payouts")
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user} - {self.bundle.name} - {self.amount}"
