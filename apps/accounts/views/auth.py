from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LogoutView, PasswordChangeView
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.accounts.forms import ResendActivationEmailForm, UserRegistrationForm
from apps.accounts.tokens import account_activation_token
from apps.accounts.utils import create_action, send_email_thread

User = get_user_model()


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
                "New user registration",
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
        create_action(
            user,
            "Account Email Activated",
            "verified their account's email address.",
            user.profile,
        )
        return redirect("bettor:dashboard")
    else:
        return render(request, "registration/activate.html", {})


class CustomPasswordChangeView(PasswordChangeView):  # login_required
    success_url = reverse_lazy("auth:password_change")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Your password was successfully changed.",
        )
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, "You have successfully logged out.")
        return super().dispatch(request, *args, **kwargs)
