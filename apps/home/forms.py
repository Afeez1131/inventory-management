from django import forms
from .models import Product, Sale
from django.forms import ValidationError, inlineformset_factory


class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["stock", "unit", "description", "total_quantity", "price_per_one"]
        labels = {"stock": "Products", "total_quantity": "Quantity"}
        widgets = {
            "stock": forms.Select(
                attrs={"class": "form-control", "placheolder": "Name of Product..."}
            ),
            "unit": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "product desciption ...",
                    "rows": "6",
                }
            ),
            "total_quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "price_per_one": forms.NumberInput(attrs={"class": "form-control"}),
        }


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["product", "qty", "payment_type",]
        labels = {
            "product": "Product",
            "customer": "Buyer of the product",
            "qty": "Quantity",
            "total_price": "Total Price",
        }
        widgets = {
            "product": forms.Select(attrs={'class': 'form-control', "id": "select-product", }),
            # "customer": forms.TextInput(attrs={"class": "form-control"}),
            "qty": forms.NumberInput(attrs={"class": "form-control"}),
            "total_price": forms.TextInput(attrs={"class": "form-control"}),
            "payment_type": forms.Select(attrs={"class": "form-control", "required": "False"}),
        }

    def clean_qty(self):
        print(self.cleaned_data)
        product = self.cleaned_data["product"]
        qty = self.cleaned_data["qty"]

        if int(qty) > product.qty_remain:
            raise ValidationError(
                "Only %s %s of %s remains in stock"
                % (product.qty_remain, product.unit, product)
            )

        return self.cleaned_data["qty"]
        
    # def clean_customer(self, *args, **kwargs):
    #     return self.cleaned_data(self, *args, **kwargs)


from apps.home.models import Invoice, Customer
from datetime import datetime

class GenerateInvoiceForm(forms.ModelForm):
    # today = datetime.now().date()
    # customers = forms.ModelMultipleChoiceField(label="Select participants*", queryset=Customer.objects.all(), widget=forms.SelectMultiple(
    #     attrs={'style': 'display: none', "data-live-search":"true"}))

    class Meta:
        model = Invoice
        fields = ("customer", "due_date", "sale", "total", "invoice_id")

    # def __int__(self, *args, **kwargs):
    #     super().__int__(*args, **kwargs)
    #     self.fields['sale']