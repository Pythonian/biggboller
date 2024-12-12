from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Bundle, Group


class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter a unique group name"),
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter group description"),
                    "rows": 2,
                }
            ),
        }
        labels = {
            "name": _("Group Name:"),
            "description": _("Description:"),
        }


class BundleCreateForm(forms.ModelForm):
    class Meta:
        model = Bundle
        fields = [
            "name",
            "price",
            "winning_percentage",
            "min_bundles_per_user",
            "max_bundles_per_user",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter a unique bundle name"),
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter bundle price"),
                }
            ),
            "winning_percentage": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter percentage between 1 - 100"),
                }
            ),
            "min_bundles_per_user": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Example: 2"),
                }
            ),
            "max_bundles_per_user": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Example: 5"),
                }
            ),
        }
        labels = {
            "name": _("Bundle Name:"),
            "price": _("Bundle Price:"),
            "winning_percentage": _("Winning Percentage:"),
            "min_bundles_per_user": _("Minimum Bundles per User:"),
            "max_bundles_per_user": _("Maximum Bundles per User:"),
        }

    def clean(self):
        cleaned_data = super().clean()
        min_bundles = cleaned_data.get("min_bundles_per_user")
        max_bundles = cleaned_data.get("max_bundles_per_user")

        # Ensure both fields are provided
        if min_bundles is None or max_bundles is None:
            raise forms.ValidationError(
                _("Both minimum and maximum bundles per user are required.")
            )
        if min_bundles > max_bundles:
            self.add_error(
                "min_bundles_per_user",
                _(
                    "Minimum bundles per user cannot exceed the maximum bundles per user."
                ),
            )


class GroupUpdateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["description", "status"]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter description"),
                    "rows": 2,
                }
            ),
        }
        labels = {
            "description": _("Description"),
            "status": _("Status"),
        }
