from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    contact_name = models.CharField(max_length=120, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=40, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Product(TimeStampedModel):
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=64, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
    )
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'supplier')
        permissions = [
            ('manage_inventory', 'Can manage inventory records'),
        ]

    def __str__(self) -> str:
        return f'{self.name} ({self.sku})'

    @property
    def is_low_stock(self) -> bool:
        return self.quantity <= self.reorder_level


class Sale(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sales')
    sold_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sales',
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if self.quantity is None or self.quantity <= 0:
            raise ValidationError('Quantity must be greater than zero.')


        available_stock = self.product.quantity
        if self.pk:
            previous = Sale.objects.filter(pk=self.pk).values('quantity').first()
            if previous:
                available_stock += previous['quantity']
        if self.quantity > available_stock:
            raise ValidationError('Not enough stock available for this sale.')

    def save(self, *args, **kwargs):
        self.full_clean()
        with transaction.atomic():
            # Calculate how much stock to deduct
            if self.pk:
                # Updating existing sale - calculate difference
                previous = Sale.objects.get(pk=self.pk)
                delta = self.quantity - previous.quantity
            else:
                # New sale - deduct full quantity
                delta = self.quantity

            # Update product stock
            product = Product.objects.get(pk=self.product_id)
            if delta > product.quantity:
                raise ValidationError('Not enough stock available for this sale.')
            product.quantity -= delta
            product.save(update_fields=['quantity', 'updated_at'])
            super().save(*args, **kwargs)
