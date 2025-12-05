from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from accounts.mixins import RolePermissionRequiredMixin

from .forms import CategoryForm, ProductForm, SaleForm, SupplierForm
from .models import Category, Product, Sale, Supplier

User = get_user_model()


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        low_stock = products.filter(quantity__lte=F('reorder_level'))
        recent_sales = Sale.objects.filter(created_at__gte=timezone.now() - timedelta(days=30))
        revenue = recent_sales.aggregate(total=Sum(F('quantity') * F('unit_price')))['total'] or 0

        context.update(
            {
                'total_products': products.count(),
                'low_stock_count': low_stock.count(),
                'low_stock_products': low_stock[:5],
                'recent_sales': recent_sales.select_related('product', 'sold_by')[:5],
                'revenue_last_30_days': revenue,
            }
        )
        return context


class ManagerAnalyticsView(LoginRequiredMixin, RolePermissionRequiredMixin, TemplateView):

    permission_required = "inventory.manage_inventory"
    template_name = "inventory/analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products = Product.objects.all()
        suppliers = Supplier.objects.all()
        sales = Sale.objects.all()

        last_30_days = timezone.now() - timedelta(days=30)
        recent_sales = sales.filter(created_at__gte=last_30_days)
        revenue_30 = recent_sales.aggregate(
            total=Sum(F("quantity") * F("unit_price"))
        )["total"] or 0

        low_stock = products.filter(quantity__lte=F("reorder_level"))

        top_products = (
            recent_sales.values("product__name")
            .annotate(total_qty=Sum("quantity"))
            .order_by("-total_qty")[:5]
        )

        sales_by_user = (
            recent_sales.values("sold_by__username")
            .annotate(
                total_sales=Count("id"),
                total_revenue=Sum(F("quantity") * F("unit_price")),
            )
            .order_by("-total_revenue")
        )

        context.update(
            {
                "total_products": products.count(),
                "total_suppliers": suppliers.count(),
                "total_sales": sales.count(),
                "revenue_last_30_days": revenue_30,
                "low_stock_count": low_stock.count(),
                "top_products": top_products,
                "sales_by_user": sales_by_user,
            }
        )
        return context


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    paginate_by = 20
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'supplier')
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        if search:
            queryset = queryset.filter(name__icontains=search)
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        context['search'] = self.request.GET.get('search', '')
        return context


class ProductCreateView(LoginRequiredMixin, RolePermissionRequiredMixin, CreateView):
    permission_required = 'inventory.manage_inventory'
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('product-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Product created successfully.')
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, RolePermissionRequiredMixin, UpdateView):
    permission_required = 'inventory.manage_inventory'
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('product-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully.')
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, RolePermissionRequiredMixin, DeleteView):
    permission_required = 'inventory.manage_inventory'
    model = Product
    template_name = 'inventory/confirm_delete.html'
    success_url = reverse_lazy('product-list')
    
    def delete(self, request, *args, **kwargs):
        messages.info(request, 'Product removed.')
        return super().delete(request, *args, **kwargs)


class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'


class SupplierCreateView(LoginRequiredMixin, RolePermissionRequiredMixin, CreateView):
    permission_required = 'inventory.manage_inventory'
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('supplier-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Supplier added.')
        return super().form_valid(form)


class SupplierUpdateView(LoginRequiredMixin, RolePermissionRequiredMixin, UpdateView):
    permission_required = 'inventory.manage_inventory'
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('supplier-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Supplier updated.')
        return super().form_valid(form)


class SupplierDeleteView(LoginRequiredMixin, RolePermissionRequiredMixin, DeleteView):
    permission_required = 'inventory.manage_inventory'
    model = Supplier
    template_name = 'inventory/confirm_delete.html'
    success_url = reverse_lazy('supplier-list')
    
    def delete(self, request, *args, **kwargs):
        messages.info(request, 'Supplier removed.')
        return super().delete(request, *args, **kwargs)


class CategoryListView(LoginRequiredMixin, RolePermissionRequiredMixin, ListView):
    permission_required = 'inventory.manage_inventory'
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'
    
class CategoryCreateView(LoginRequiredMixin, RolePermissionRequiredMixin, CreateView):
    permission_required = 'inventory.manage_inventory'
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('category-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Category created.')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, RolePermissionRequiredMixin, UpdateView):
    permission_required = 'inventory.manage_inventory'
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('category-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Category updated.')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, RolePermissionRequiredMixin, DeleteView):
    permission_required = 'inventory.manage_inventory'
    model = Category
    template_name = 'inventory/confirm_delete.html'
    success_url = reverse_lazy('category-list')
    
    def delete(self, request, *args, **kwargs):
        if self.get_object().products.exists():
            messages.error(request, 'Cannot delete a category that still has products.')
            return redirect('category-list')
        messages.info(request, 'Category removed.')
        return super().delete(request, *args, **kwargs)


class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'inventory/sale_list.html'
    context_object_name = 'sales'

    def get_queryset(self):
        queryset = Sale.objects.select_related('product', 'sold_by')
        product_id = self.request.GET.get('product')
        user_id = self.request.GET.get('user')
        start = self.request.GET.get('start')
        end = self.request.GET.get('end')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if user_id:
            queryset = queryset.filter(sold_by_id=user_id)
        if start:
            queryset = queryset.filter(created_at__date__gte=start)
        if end:
            queryset = queryset.filter(created_at__date__lte=end)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['users'] = User.objects.all()
        context['filters'] = self.request.GET
        return context


class SaleCreateView(LoginRequiredMixin, CreateView):
    template_name = 'inventory/sale_form.html'
    form_class = SaleForm
    success_url = reverse_lazy('sale-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        sale = form.save(commit=False)
        sale.sold_by = self.request.user
        sale.save()
        messages.success(self.request, 'Sale recorded.')
        return redirect(self.success_url)
