import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class GroupManager(models.Manager):
    def running(self):
        return self.filter(status=Group.Status.RUNNING)

    def closed(self):
        return self.filter(status=Group.Status.CLOSED)


class Group(models.Model):
    """
    Represents a betting group created by an admin.
    Each group has a unique bundle associated with it.
    """

    class Status(models.TextChoices):
        RUNNING = "R", _("Running")
        CLOSED = "C", _("Closed")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
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
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("Timestamp when the group was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("Timestamp when the group was last updated."),
    )

    objects = GroupManager()

    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("administrator:groups_detail", args=[self.id])


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


class Bundle(models.Model):
    """
    Defines the pricing and potential winnings for a specific group.
    Each bundle is uniquely associated with one group.
    """

    class Status(models.TextChoices):
        PENDING = "P", _("Pending")
        WON = "W", _("Won")
        LOST = "L", _("Lost")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
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
    minimum_win_multiplier = models.PositiveSmallIntegerField(
        verbose_name=_("Minimum Win Multiplier"),
        help_text=_("Minimum multiplier value to calculate minimum potential wins."),
        validators=[MinValueValidator(1)],
    )
    maximum_win_multiplier = models.PositiveSmallIntegerField(
        verbose_name=_("Maximum Win Multiplier"),
        help_text=_("Maximum multiplier value to calculate maximum potential wins."),
        validators=[MinValueValidator(1)],
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
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("Timestamp when the bundle was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("Timestamp when the bundle was last updated."),
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
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("administrator:bundles_detail", args=[self.id])

    @property
    def participants_count(self):
        """
        Return the number of participants who have purchased this bundle.
        """
        return self.participants.count()

    def clean(self):
        if self.maximum_win_multiplier <= self.minimum_win_multiplier:
            raise ValidationError(
                {
                    "maximum_win_multiplier": _(
                        "Maximum win multiplier must be greater than the minimum win multiplier."
                    )
                }
            )

        if self.min_bundles_per_user >= self.max_bundles_per_user:
            raise ValidationError(
                {
                    "min_bundles_per_user": _(
                        "Minimum bundles per user cannot exceed the maximum bundles per user."
                    )
                }
            )

    @property
    def potential_min_win(self):
        """
        Calculate the minimum potential win dynamically.
        """
        return self.price * self.minimum_win_multiplier * self.min_bundles_per_user

    @property
    def potential_max_win(self):
        """
        Calculate the maximum potential win dynamically.
        """
        return self.price * self.maximum_win_multiplier * self.max_bundles_per_user
