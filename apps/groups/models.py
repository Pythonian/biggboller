import uuid

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class GroupManager(models.Manager):
    def running(self):
        return self.filter(status=Group.Status.RUNNING)

    def closed(self):
        return self.filter(status=Group.Status.CLOSED)


class Group(TimeStampedModel):
    """
    Represents a betting group created by an admin.
    Each group has a unique bundle associated with it.
    """

    class Status(models.TextChoices):
        RUNNING = "R", _("Running")
        CLOSED = "C", _("Closed")

    group_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Group Name"),
        help_text=_("Enter a unique name for the betting group."),
    )
    description = models.TextField(
        verbose_name=_("Description"),
        max_length=140,
        help_text=_("Provide a detailed description of the betting group."),
    )
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.RUNNING,
        verbose_name=_("Status"),
        help_text=_("Select a status for the betting group."),
        db_index=True,
    )
    bettors = models.ManyToManyField(
        get_user_model(),
        related_name="bet_groups",
        blank=True,
        verbose_name=_("Bettors"),
        help_text=_("Users who are part of this group."),
    )

    objects = GroupManager()

    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "groups:groups_detail",
            args=[self.group_id],
        )


class BundleManager(models.Manager):
    def pending(self):
        return self.filter(
            status=Bundle.Status.PENDING,
            group__status=Group.Status.RUNNING,
        )

    def won(self):
        return self.filter(status=Bundle.Status.WON)

    def lost(self):
        return self.filter(status=Bundle.Status.LOST)


class Bundle(TimeStampedModel):
    """
    Defines the pricing and potential winnings for a specific group.
    Each bundle is uniquely associated with one group.
    """

    class Status(models.TextChoices):
        PENDING = "P", _("Pending")
        WON = "W", _("Won")
        LOST = "L", _("Lost")

    MAX_ROUNDS = 4
    current_round = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Current Round"),
        help_text=_("The current round of the bundle (1-4)."),
    )
    round_outcomes = models.JSONField(
        default=dict,
        verbose_name=_("Round Outcomes"),
        help_text=_(
            "A dictionary storing the outcomes of each round, e.g., {1: 'L', 2: 'W'}."
        ),
    )

    bundle_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="bundle",
        verbose_name=_("Group"),
        help_text=_("Select the group this bundle is associated with."),
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Bundle Name"),
        help_text=_("Enter a unique name for the group bundle."),
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Bundle Price"),
        help_text=_("Enter the price for one bundle."),
    )
    winning_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Winning Percentage"),
        help_text=_(
            "Enter the percentage of the bundle price that will be returned as winnings. E.g., 20 for 20%."
        ),
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    min_bundles_per_user = models.PositiveIntegerField(
        verbose_name=_("Minimum Bundles per User"),
        help_text=_("Minimum number of bundles a user can purchase."),
        validators=[MinValueValidator(1)],
    )
    max_bundles_per_user = models.PositiveIntegerField(
        verbose_name=_("Maximum Bundles per User"),
        help_text=_("Maximum number of bundles a user can purchase."),
        validators=[MinValueValidator(1)],
    )
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Status"),
        help_text=_("Current status of the bundle."),
    )
    participants = models.ManyToManyField(
        get_user_model(),
        related_name="bundles",
        blank=True,
        verbose_name=_("Participants"),
        help_text=_("Users who have purchased this bundle."),
    )

    objects = BundleManager()

    class Meta:
        verbose_name = _("Bundle")
        verbose_name_plural = _("Bundles")
        ordering = ["-created"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "groups:bundles_detail",
            args=[self.bundle_id],
        )

    @property
    def participants_count(self):
        """
        Return the number of participants who have purchased this bundle.
        """
        return self.participants.count()


class Purchase(TimeStampedModel):
    """Represents a payment (stake) made by a bettor for a bundle."""

    class Status(models.TextChoices):
        PENDING = "P", _("Pending")
        APPROVED = "A", _("Approved")
        CANCELLED = "C", _("Cancelled")

    purchase_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchases",
        verbose_name=_("User"),
    )
    bundle = models.ForeignKey(
        "Bundle",
        on_delete=models.CASCADE,
        related_name="purchases",
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
        _("Payout Amount"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    reference = models.CharField(
        _("Reference"),
        max_length=20,
        unique=True,
        help_text=_("Unique ID of the bundle purchase transaction"),
    )
    status = models.CharField(
        _("Status"),
        max_length=1,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        verbose_name = _("Purchase")
        verbose_name_plural = _("Purchases")
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user} - {self.bundle.name} - {self.amount}"

    def get_absolute_url(self):
        return reverse("bettor:purchase_successful", args=[self.purchase_id])

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


class Payout(TimeStampedModel):
    """Represents a payout for a bettor after a bundle is won."""

    class Status(models.TextChoices):
        APPROVED = "A", _("Approved")
        CANCELLED = "C", _("Cancelled")

    payout_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
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
        help_text=_("The winning amount the bettor is paid."),
    )
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.APPROVED,
        verbose_name=_("Status"),
    )

    class Meta:
        verbose_name = _("Payout")
        verbose_name_plural = _("Payouts")
        ordering = ["-created"]

    def __str__(self):
        return f"Payout: {self.user.username} - Amount: {self.amount}"
