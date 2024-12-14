from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from apps.accounts.forms import UserLoginForm
from apps.accounts.views.auth import (
    account_activation_sent,
    resend_activation,
    account_activate,
    register,
    CustomLoginView,
    CustomPasswordChangeView,
    CustomLogoutView,
)
from django.views.generic.base import RedirectView

app_name = "auth"

urlpatterns = [
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path(
        "login/",
        CustomLoginView.as_view(
            redirect_authenticated_user=True,
            authentication_form=UserLoginForm,
        ),
        name="login",
    ),
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
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            success_url=reverse_lazy("auth:password_reset_done")
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password_reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            success_url=reverse_lazy("auth:password_reset_complete")
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "password_change/",
        CustomPasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "",
        RedirectView.as_view(url="auth:login", permanent=True),
        name="account",
    ),
]
