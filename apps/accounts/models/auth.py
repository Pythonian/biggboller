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
    is_banned = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return self.user.username

    def get_screen_name(self):
        try:
            if self.user.get_full_name():
                return self.user.get_full_name()
            else:
                return self.user.username
        except:
            return self.user.username
