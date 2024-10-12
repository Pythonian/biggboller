from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.accounts.forms import UserRegistrationForm, ResendActivationEmailForm
from apps.accounts.tokens import account_activation_token


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
            # user.profile.data = form.cleaned_data.get("data")
            # user.save()
            current_site = get_current_site(request)

            if request.is_secure():
                protocol = "https"
            else:
                protocol = "http"

            subject = render_to_string(
                "registration/account_activation_subject.txt",
                {"site_name": current_site.name},
            )

            message = render_to_string(
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
            user.email_user(subject=subject, message=message)
            return redirect("auth:account_activation_sent")
        else:
            messages.error(
                request,
                "An error occured while trying to create your account.",
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
            user = User.objects.filter(email__iexact=email, is_active=False)
            if not user.count():
                form._errors["email"] = [
                    "Account for email address is not registered or already activated."
                ]
            current_site = get_current_site(request)
            if request.is_secure():
                protocol = "https"
            else:
                protocol = "http"
            subject = render_to_string(
                "registration/account_activation_subject.txt",
                {"site_name": current_site.name},
            )

            message = render_to_string(
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
            user.email_user(subject, message)
            return redirect("account_activation_sent")
        else:
            messages.error(
                request,
                "An error occured while sending your account activation email.",
            )
            return redirect("auth:resend_activation")
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
        login(request, user)
        messages.success(
            request,
            "Your account has been successully activated.",
        )
        return redirect("bettor:dashboard")
    else:
        return render(request, "registration/activate.html", {})


@login_required
def disable(request):
    user = request.user
    if request.method == "POST":
        # Disable the user's password
        user.set_unusable_password()
        # Disable the user's account
        user.is_active = False
        user.save()
        logout(request)
        return redirect("core:home")

    template = "accounts/disable.html"
    context = {}

    return render(request, template, context)
