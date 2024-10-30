from django import forms
from django.contrib.auth import get_user_model
from apps.accounts.models import Profile

User = get_user_model()


class UserUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required
        for field in self.fields.values():
            field.required = True

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        help_texts = {
            "username": "Username must be alphanumeric only.",
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError(
                "A user with that email already exists.",
            )
        return email


class ProfileUpdateForm(forms.ModelForm):
    payout_information = forms.CharField(
        required=True,
        widget=forms.Textarea(),
    )

    class Meta:
        model = Profile
        fields = ["phone_number", "payout_information"]
