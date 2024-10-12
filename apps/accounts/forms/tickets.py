from django import forms
from apps.accounts.models import Ticket, Reply


class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["subject", "description"]
        widgets = {
            "subject": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Subject"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Describe your issue"}
            ),
        }


class TicketReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Your reply"}
            ),
        }
