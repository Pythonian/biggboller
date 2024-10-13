from django import forms
from apps.accounts.models import Bundle


class BundlePurchaseForm(forms.Form):
    bundle = forms.ModelChoiceField(
        queryset=Bundle.objects.filter(status=Bundle.Status.PENDING),
        label="Select Bundle",
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "bundle-select",
            }
        ),
    )
    quantity = forms.IntegerField(
        min_value=1,
        label="Quantity",
        initial=1,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "id": "quantity-input"}
        ),
    )
    total_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Total Amount",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "total-amount",
                "readonly": "readonly",
            }
        ),
    )

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        bundle = self.cleaned_data.get("bundle")
        if bundle:
            if quantity < bundle.min_bundles_per_user:
                raise forms.ValidationError(
                    f"Minimum {bundle.min_bundles_per_user} bundles required."
                )
            if quantity > bundle.max_bundles_per_user:
                raise forms.ValidationError(
                    f"Maximum {bundle.max_bundles_per_user} bundles allowed."
                )
        return quantity
