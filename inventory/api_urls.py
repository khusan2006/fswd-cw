"""API URL routes for inventory resources."""

from django.urls import include, path
from rest_framework import routers

from .api import (
    CategoryViewSet,
    ProductViewSet,
    SaleViewSet,
    SupplierViewSet,
)

router = routers.DefaultRouter()
router.register("categories", CategoryViewSet, basename="api-category")
router.register("suppliers", SupplierViewSet, basename="api-supplier")
router.register("products", ProductViewSet, basename="api-product")
router.register("sales", SaleViewSet, basename="api-sale")

urlpatterns = [
    path("", include(router.urls)),
]


