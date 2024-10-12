from django.urls import include, path
from apps.accounts.views.auth import (
    account_activation_sent,
    resend_activation,
    account_activate,
    register,
)
from django.views.generic.base import RedirectView

app_name = "auth"

urlpatterns = [
    path(
        "activation/sent/",
        account_activation_sent,
        name="account_activation_sent",
    ),
    path(
        "activate/resend/",
        resend_activation,
        name="resend_activation",
    ),
    path(
        "activate/<slug:uidb64>/<slug:token>/",
        account_activate,
        name="activate",
    ),
    path("register/", register, name="register"),
    path(
        "",
        RedirectView.as_view(url="auth:login", permanent=True),
        name="account",
    ),
    path("", include("django.contrib.auth.urls")),
]
