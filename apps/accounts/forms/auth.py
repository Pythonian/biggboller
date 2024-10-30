from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator
# from .models import Profile

User = get_user_model()


USERNAME_REGEX = "^[a-zA-Z0-9]*$"


DISALLOWED_USERNAMES = [
    "activate",
    "account",
    "admin",
    "about",
    "administrator",
    "activity",
    "account",
    "auth",
    "authentication",
    "deactivated",
    "notifications",
    "verified",
    "unverified",
    "banned",
    "active",
    "suspend",
    "unban",
]


class UserLoginForm(AuthenticationForm):
    """Custom Login form that extends Django's Login form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    username = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(),
    )
    password = forms.CharField(widget=forms.PasswordInput())


class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=USERNAME_REGEX,
                message="Your username contains invalid characters.",
                code="invalid_username",
            )
        ],
        help_text="Username must be alphanumeric only.",
        required=True,
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text="Enter a valid email address.",
    )
    phone_number = forms.CharField(
        label="Phone number",
        max_length=11,
        required=True,
        help_text="Enter a valid phone number.",
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Repeat Password",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
        ]

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise forms.ValidationError("Password fields do not match.")
        return cd["password2"]

    def clean_username(self):
        username = self.cleaned_data.get("username").lower()
        if username in DISALLOWED_USERNAMES:
            raise forms.ValidationError(
                "You are not allowed to make use of this username."
            )
        if len(username) < 4:
            raise forms.ValidationError(
                "Your username must not be less than 4 (four) characters."
            )
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "A user with that email already exists.",
            )
        return email


class ResendActivationEmailForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text="Enter your email address.",
    )
