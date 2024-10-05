from django import forms
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Group


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
            "status": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "description": _("Description"),
            "status": _("Status"),
        }
