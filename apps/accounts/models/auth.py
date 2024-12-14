from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("user"),
    )
    email_confirmed = models.BooleanField(
        _("email confirmed?"),
        default=False,
        help_text="Determine if the User's email has been confirmed.",
    )
    verified_account = models.BooleanField(
        _("verified account?"),
        default=False,
    )
    phone_number = models.CharField(
        _("phone number"),
        max_length=11,
    )
    payout_information = models.TextField(
        _("Bank Account Information"),
        blank=True,
        help_text=_("Bank account information for Withdrawals"),
    )
    is_banned = models.BooleanField(default=False)
    account_activated_at = models.DateTimeField(
        _("Account Activation Date"),
        null=True,
        blank=True,
        help_text="The date when the user activated their account.",
    )
    transaction_pin = models.CharField(
        max_length=128,
        blank=True,
        help_text=_("User's 6-digit transaction PIN (hashed)."),
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return self.user.username


class LoginHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    browser = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    os = models.CharField(max_length=50, null=True, blank=True)
    device = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ["-login_time"]

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
