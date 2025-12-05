from rest_framework import permissions, serializers, viewsets

from accounts.models import User
from .models import Category, Product, Sale, Supplier


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at", "updated_at"]


class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "contact_name",
            "contact_email",
            "contact_phone",
            "address",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ProductSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(source="category.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "sku",
            "category",
            "category_name",
            "supplier",
            "supplier_name",
            "description",
            "quantity",
            "reorder_level",
            "price",
            "is_active",
            "is_low_stock",
            "created_at",
            "updated_at",
        ]


class SaleSerializer(serializers.ModelSerializer):

    sold_by = serializers.PrimaryKeyRelatedField(read_only=True)
    sold_by_username = serializers.CharField(source="sold_by.username", read_only=True)

    class Meta:
        model = Sale
        fields = [
            "id",
            "product",
            "sold_by",
            "sold_by_username",
            "quantity",
            "unit_price",
            "notes",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        if not request or not isinstance(request.user, User):
            raise serializers.ValidationError("Authenticated user required to record a sale.")
        validated_data["sold_by"] = request.user
        return super().create(validated_data)


class BaseViewSet(viewsets.ModelViewSet):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoryViewSet(BaseViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SupplierViewSet(BaseViewSet):

    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class ProductViewSet(BaseViewSet):

    queryset = Product.objects.select_related("category", "supplier").all()
    serializer_class = ProductSerializer


class SaleViewSet(BaseViewSet):

    queryset = Sale.objects.select_related("product", "sold_by").all()
    serializer_class = SaleSerializer


