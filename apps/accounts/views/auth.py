import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import PasswordChangeView  # , LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_bytes, force_str
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.views import LoginView
from django.utils import timezone

from user_agents import parse

from apps.accounts.models import LoginHistory

from apps.accounts.forms import ResendActivationEmailForm, UserRegistrationForm
from apps.accounts.tokens import account_activation_token
from apps.accounts.utils import create_action, send_email_thread

import logging

logger = logging.getLogger(__name__)

User = get_user_model()


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_location_from_ip(ip_address):
    if ip_address == "127.0.0.1":
        return "Localhost"
    try:
        response = requests.get(f"https://ipinfo.io/{ip_address}/json")
        data = response.json()
        location = f"{data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}, {data.get('country', 'Unknown')}"
    except Exception:
        location = "Unknown"
    return location


class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)  # noqa: F841
        user = self.request.user
        current_site = get_current_site(self.request)

        # Retrieve IP address
        ip_address = get_client_ip(self.request)

        # Parse user agent to retrieve browser, OS, and device info
        user_agent = parse(self.request.META.get("HTTP_USER_AGENT", ""))
        browser_info = (
            f"{user_agent.browser.family} {user_agent.browser.version_string}"
        )
        os_info = user_agent.os.family
        device_info = (
            user_agent.device.family
            if user_agent.device.family != "Other"
            else "Unknown Device"
        )
        location = get_location_from_ip(ip_address)

        # Check for duplicate login history
        last_login = LoginHistory.objects.filter(user=user).last()
        if not last_login or (
            (timezone.now() - last_login.login_time).total_seconds() > 60
            or last_login.ip_address != ip_address
            or last_login.browser != browser_info
        ):
            # Create LoginHistory entry if conditions are met
            LoginHistory.objects.create(
                user=user,
                ip_address=ip_address,
                location=location,
                browser=browser_info,
                os=os_info,
                device=device_info,
            )

            current_time = timezone.now()
            formatted_time = current_time.strftime("%B %d, %Y %I:%M%p")
            create_action(
                user,
                "New Login Detected",
                f"logged into their account at {formatted_time}.",
                user.profile,
            )

            # Set context for the email template
            context = {
                "user": user,
                "login_time": timezone.now(),
                "ip_address": ip_address,
                "location": location,
                "device": device_info,
                "browser": browser_info,
                "os": os_info,
                "site_name": current_site.name,
            }

            # Send login notification email
            subject = f"New Login Alert from {current_site.name}"
            html_message = render_to_string(
                "registration/login_notification.html",
                context,
            )
            text_message = strip_tags(html_message)

            try:
                send_email_thread(
                    subject,
                    text_message,
                    html_message,
                    user.email,
                    user.get_full_name(),
                )
            except Exception as e:
                logger.exception(f"Login email notification failed: {e}")

        redirect_url = self.request.GET.get("next") or settings.LOGIN_REDIRECT_URL
        return redirect(redirect_url)


def register(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.set_password(form.cleaned_data["password"])
            # User shouldn't log in before confirming email
            user.is_active = False
            user.save()
            # Load profile instance created by the signal
            user.refresh_from_db()
            user.profile.phone_number = form.cleaned_data.get("phone_number")
            user.save()
            current_site = get_current_site(request)

            protocol = "https" if request.is_secure() else "http"

            subject = render_to_string(
                "registration/account_activation_subject.txt",
                {"site_name": current_site.name},
            ).strip()

            text_message = render_to_string(
                "registration/account_activation_email.txt",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "protocol": protocol,
                    "site_name": current_site.name,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            ).strip()

            html_message = render_to_string(
                "registration/account_activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "protocol": protocol,
                    "site_name": current_site.name,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )

            # Send email via Mailjet in a separate thread
            send_email_thread(
                subject,
                text_message,
                html_message,
                user.email,
                user.get_full_name(),
            )

            create_action(
                user,
                "New User Registration",
                "registered for an account.",
                user.profile,
            )
            return redirect("auth:account_activation_sent")
        else:
            messages.error(
                request,
                "An error occurred while trying to create your account.",
            )
            return render(
                request,
                "registration/register.html",
                {"form": form},
            )
    else:
        form = UserRegistrationForm()

    template = "registration/register.html"
    context = {"form": form}

    return render(request, template, context)


def resend_activation(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    # TODO: test out this resend activation implementation

    if request.method == "POST":
        form = ResendActivationEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            user = User.objects.filter(
                email__iexact=email,
                is_active=False,
            ).first()
            if not user:
                form.add_error(
                    "email",
                    "Account for this email is not registered or already activated.",
                )
                return render(
                    request,
                    "registration/resend_activation.html",
                    {"form": form},
                )

            current_site = get_current_site(request)
            protocol = "https" if request.is_secure() else "http"

            subject = render_to_string(
                "registration/account_activation_subject.txt",
                {"site_name": current_site.name},
            ).strip()

            text_message = render_to_string(
                "registration/account_activation_email.txt",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "protocol": protocol,
                    "site_name": current_site.name,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            ).strip()

            html_message = render_to_string(
                "registration/account_activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "protocol": protocol,
                    "site_name": current_site.name,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )

            # Send email via Mailjet in a separate thread
            send_email_thread(
                subject,
                text_message,
                html_message,
                user.email,
                user.get_full_name(),
            )

            return redirect("auth:account_activation_sent")
        else:
            messages.error(
                request,
                "An error occurred while sending your activation email.",
            )
            return render(
                request, "registration/resend_activation.html", {"form": form}
            )
    else:
        form = ResendActivationEmailForm()

    template = "registration/resend_activation.html"
    context = {
        "form": form,
    }

    return render(request, template, context)


def account_activation_sent(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    template = "registration/account_activation_sent.html"
    context = {}

    return render(request, template, context)


def account_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.profile.account_activated_at = timezone.now()
        user.save()
        login(
            request,
            user,
            backend="apps.accounts.authentication.EmailAuthenticationBackend",
        )
        messages.success(
            request,
            "Your account has been successully activated.",
        )

        # Send the email
        current_site = get_current_site(request)
        protocol = "https" if request.is_secure() else "http"

        subject = render_to_string(
            "registration/account_activation_success_subject.txt",
            {"site_name": current_site.name},
        ).strip()

        text_message = render_to_string(
            "registration/account_activation_success_email.txt",
            {
                "user": user,
                "domain": current_site.domain,
                "protocol": protocol,
                "site_name": current_site.name,
            },
        ).strip()

        html_message = render_to_string(
            "registration/account_activation_success_email.html",
            {
                "user": user,
                "domain": current_site.domain,
                "protocol": protocol,
                "site_name": current_site.name,
            },
        )

        # Send email
        send_email_thread(
            subject,
            text_message,
            html_message,
            user.email,
            user.get_full_name(),
        )

        create_action(
            user,
            "Account Email Activated",
            "verified their account's email address.",
            user.profile,
        )
        return redirect("bettor:dashboard")
    else:
        return render(request, "registration/activate.html", {})


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy("core:dashboard")

    def form_valid(self, form):
        user = self.request.user
        subject = _("Password Changed Successfully")
        html_message = render_to_string(
            "registration/password_change_confirmation.html",
            {"user": user},
        )
        text_message = strip_tags(html_message)

        try:
            send_email_thread(
                subject,
                text_message,
                html_message,
                user.email,
                user.get_full_name(),
            )
        except Exception as e:
            logger.error(f"Error sending password change email: {e}")

        messages.success(
            self.request,
            _("Your password was successfully changed."),
        )
        return super().form_valid(form)


# class CustomLogoutView(LoginRequiredMixin, LogoutView):
#     def dispatch(self, request, *args, **kwargs):
#         if request.user.is_authenticated:
#             messages.success(request, "You have successfully logged out.")
#         return super().dispatch(request, *args, **kwargs)
