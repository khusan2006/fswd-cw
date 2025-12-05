from django.urls import path

from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('analytics/', views.ManagerAnalyticsView.as_view(), name='analytics'),
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product-edit'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    path('suppliers/', views.SupplierListView.as_view(), name='supplier-list'),
    path('suppliers/create/', views.SupplierCreateView.as_view(), name='supplier-create'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier-edit'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier-delete'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category-edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),
    path('sales/', views.SaleListView.as_view(), name='sale-list'),
    path('sales/create/', views.SaleCreateView.as_view(), name='sale-create'),
]


