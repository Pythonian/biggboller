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
        REJECTED = "R", _("Rejected")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
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
    reference = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Payment Reference"),
    )
    paystack_id = models.CharField(
        max_length=150,
        blank=True,
    )
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
    def potential_min_win(self):
        """
        Calculate the minimum potential win dynamically.
        """
        return self.amount * self.bundle.minimum_win_multiplier

    @property
    def potential_max_win(self):
        """
        Calculate the maximum potential win dynamically.
        """
        return self.amount * self.bundle.maximum_win_multiplier
