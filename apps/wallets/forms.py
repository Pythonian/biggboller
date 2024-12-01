from django import forms
from decimal import Decimal
from .models import Deposit, Withdrawal


class DepositForm(forms.ModelForm):
    amount = forms.DecimalField(
        required=True,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter amount to deposit"}
        ),
    )
    description = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Optional description"}
        ),
    )

    class Meta:
        model = Deposit
        fields = ["amount", "description"]

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount < Decimal("1000.00"):
            raise forms.ValidationError("Minimum deposit amount is 1000 Naira.")
        return amount


class WithdrawalForm(forms.ModelForm):
    amount = forms.DecimalField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter amount to withdraw",
            }
        ),
    )
    description = forms.CharField(
        max_length=300,
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Withdrawal description",
            }
        ),
    )

    class Meta:
        model = Withdrawal
        fields = ["amount", "description"]
