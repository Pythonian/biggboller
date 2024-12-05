from django import forms
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from .models import Deposit, Withdrawal


class TransactionForm(forms.ModelForm):
    def add_widget_attrs(self, field_name, attrs):
        """Add custom attributes to a form field's widget."""
        field = self.fields[field_name]
        field.widget.attrs.update(attrs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_widget_attrs(
            "amount",
            {
                "class": "form-control",
                "placeholder": "Enter amount",
            },
        )
        self.add_widget_attrs(
            "description",
            {
                "class": "form-control",
                "placeholder": "Enter description",
                "rows": 4,
            },
        )


class DepositForm(TransactionForm):
    class Meta:
        model = Deposit
        fields = ["amount", "description"]

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount < Decimal("1000.00"):
            raise forms.ValidationError("Minimum deposit amount is ₦1,000.")
        return amount


class WithdrawalForm(TransactionForm):
    """
    Form to handle withdrawal requests with enhanced validation.
    """

    def __init__(self, *args, **kwargs):
        self.wallet_balance = kwargs.pop("wallet_balance", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Withdrawal
        fields = ["amount", "description"]

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount <= 0:
            raise forms.ValidationError(
                _("Withdrawal amount must be greater than zero.")
            )
        if self.wallet_balance is not None and amount > self.wallet_balance:
            raise forms.ValidationError(
                _("Withdrawal amount exceeds your wallet balance.")
            )
        return amount
