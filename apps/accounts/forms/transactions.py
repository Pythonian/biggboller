from django import forms


class BundlePurchaseForm(forms.Form):
    quantity = forms.ChoiceField(label="Quantity", choices=[])

    def __init__(self, *args, **kwargs):
        self.bundle = kwargs.pop("bundle", None)
        super().__init__(*args, **kwargs)
        if self.bundle:
            min_qty = self.bundle.min_bundles_per_user
            max_qty = self.bundle.max_bundles_per_user
            self.fields["quantity"].choices = [
                (i, i) for i in range(min_qty, max_qty + 1)
            ]
        else:
            self.fields["quantity"].choices = []

    def clean_quantity(self):
        quantity = int(self.cleaned_data.get("quantity"))

        # Check if bundle is available and validate quantity range
        if self.bundle:
            min_qty = self.bundle.min_bundles_per_user
            max_qty = self.bundle.max_bundles_per_user
            if not (min_qty <= quantity <= max_qty):
                raise forms.ValidationError(
                    f"Please select a quantity between {min_qty} and {max_qty}."
                )
        return quantity
