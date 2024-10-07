from django import forms
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Bundle, Group


class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": _("Enter group name")}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter group description"),
                    "rows": 4,
                }
            ),
        }
        labels = {
            "name": _("Group Name"),
            "description": _("Description"),
        }


class BundleCreateForm(forms.ModelForm):
    class Meta:
        model = Bundle
        fields = [
            "name",
            "price",
            "minimum_win_multiplier",
            "maximum_win_multiplier",
            "min_bundles_per_user",
            "max_bundles_per_user",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter bundle name"),
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter bundle price"),
                }
            ),
            "minimum_win_multiplier": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter minimum win multiplier"),
                }
            ),
            "maximum_win_multiplier": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter maximum win multiplier"),
                }
            ),
            "min_bundles_per_user": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter minimum bundles per user"),
                }
            ),
            "max_bundles_per_user": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter maximum bundles per user"),
                }
            ),
        }
        labels = {
            "name": _("Bundle Name"),
            "price": _("Bundle Price"),
            "minimum_win_multiplier": _("Minimum Win Multiplier"),
            "maximum_win_multiplier": _("Maximum Win Multiplier"),
            "min_bundles_per_user": _("Minimum Bundles per User"),
            "max_bundles_per_user": _("Maximum Bundles per User"),
        }

    def clean(self):
        cleaned_data = super().clean()
        min_multiplier = cleaned_data.get("minimum_win_multiplier")
        max_multiplier = cleaned_data.get("maximum_win_multiplier")
        min_bundles = cleaned_data.get("min_bundles_per_user")
        max_bundles = cleaned_data.get("max_bundles_per_user")

        if min_multiplier and max_multiplier:
            if max_multiplier <= min_multiplier:
                self.add_error(
                    "maximum_win_multiplier",
                    _(
                        "Maximum win multiplier must be greater than the minimum win multiplier."
                    ),
                )

        if min_bundles and max_bundles:
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
                    "placeholder": _("Enter new description"),
                    "rows": 4,
                }
            ),
        }
        labels = {
            "description": _("Description"),
            "status": _("Status"),
        }
