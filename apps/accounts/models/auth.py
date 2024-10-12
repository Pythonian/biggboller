from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("user"),
    )
    about = models.CharField(
        _("about"),
        blank=True,
        max_length=140,
        help_text=_("Tell us about yourself in 140 characters."),
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
    location = models.CharField(
        _("location"),
        max_length=30,
        blank=True,
        null=True,
    )
    is_banned = models.BooleanField(default=False)

    class Meta:
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
