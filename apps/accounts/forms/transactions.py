from django import forms


class BundlePurchaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        bundle = kwargs.pop("bundle", None)
        super().__init__(*args, **kwargs)
        if bundle:
            min_qty = bundle.min_bundles_per_user
            max_qty = bundle.max_bundles_per_user
            self.fields["quantity"].choices = [
                (i, i) for i in range(min_qty, max_qty + 1)
            ]
        else:
            # Optionally, handle cases where bundle is not provided
            self.fields["quantity"].choices = []

    quantity = forms.ChoiceField(
        label="Quantity",
        # This will be populated dynamically in the __init__ method
        choices=[],
    )
