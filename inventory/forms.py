from django import forms

from .models import Category, Product, Sale, Supplier


class StyledForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            existing_classes = widget.attrs.get('class', '')
            widget.attrs['class'] = f'{existing_classes} w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-slate-500'.strip()


class CategoryForm(StyledForm):
    class Meta:
        model = Category
        fields = ('name', 'description')
        labels = {
            'name': 'Category Name',
            'description': 'Description',
        }
        help_texts = {
            'description': 'Optional description for this category.',
        }


class SupplierForm(StyledForm):
    class Meta:
        model = Supplier
        fields = (
            'name',
            'contact_name',
            'contact_email',
            'contact_phone',
            'address',
            'is_active',
        )
        labels = {
            'name': 'Supplier Name',
            'contact_name': 'Contact Person',
            'contact_email': 'Email',
            'contact_phone': 'Phone',
            'address': 'Address',
            'is_active': 'Active',
        }


class ProductForm(StyledForm):
    class Meta:
        model = Product
        fields = (
            'name',
            'sku',
            'category',
            'supplier',
            'description',
            'quantity',
            'reorder_level',
            'price',
            'is_active',
        )
        labels = {
            'name': 'Product Name',
            'sku': 'SKU',
            'category': 'Category',
            'supplier': 'Supplier',
            'description': 'Description',
            'quantity': 'Quantity in Stock',
            'reorder_level': 'Reorder Level',
            'price': 'Price',
            'is_active': 'Active',
        }
        help_texts = {
            'sku': 'Stock Keeping Unit - unique identifier for this product.',
            'reorder_level': 'Alert when stock falls below this number.',
        }

    def clean_reorder_level(self):
        reorder = self.cleaned_data.get('reorder_level')
        if reorder is not None and reorder < 0:
            raise forms.ValidationError('Reorder level cannot be negative.')
        return reorder


class SaleForm(StyledForm):
    class Meta:
        model = Sale
        # `unit_price` is populated from the selected product automatically.
        fields = ('product', 'quantity', 'unit_price', 'notes')
        labels = {
            'product': 'Product',
            'quantity': 'Quantity Sold',
            'unit_price': 'Unit Price',
            'notes': 'Notes',
        }
        help_texts = {
            'unit_price': 'Automatically taken from the selected product.',
            'notes': 'Optional notes about this sale.',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['unit_price'].required = False
        self.fields['unit_price'].widget = forms.HiddenInput()
        if not user or not user.is_manager():
            self.fields['product'].queryset = self.fields['product'].queryset.filter(is_active=True)

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get('product')
        quantity = cleaned.get('quantity')

        if product and quantity:
            if quantity <= 0:
                self.add_error('quantity', 'Quantity must be greater than zero.')
            elif quantity > product.quantity:
                self.add_error(
                    'quantity',
                    f'Not enough stock available. Current stock: {product.quantity}.',
                )

            cleaned['unit_price'] = product.price
            self.instance.unit_price = product.price

        return cleaned

