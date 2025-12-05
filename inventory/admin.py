from django.contrib import admin

from .models import Category, Product, Sale, Supplier


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'contact_phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'contact_email')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'supplier', 'quantity', 'reorder_level', 'is_active')
    list_filter = ('category', 'supplier', 'is_active')
    search_fields = ('name', 'sku')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'unit_price', 'sold_by', 'created_at')
    list_filter = ('product', 'sold_by')
    search_fields = ('product__name', 'sold_by__username')
