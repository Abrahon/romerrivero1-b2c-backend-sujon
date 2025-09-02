from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
import csv

from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer


# ==============================
# Admin Views (CRUD for Category)
# ==============================
class AdminCategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]


# ==============================
# Admin Views - CRUD for Product
# ==============================
class AdminProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save()


class AdminProductCreateUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"        # match model field
    lookup_url_kwarg = "id"    # match URL kwarg <uuid:id>

    # Update product
    def update(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Delete product
    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        return Response({"message": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# ==============================
# User Views
# ==============================
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="category__name", lookup_expr="iexact")

    class Meta:
        model = Product
        fields = ["category"]


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"
    lookup_url_kwarg = "id"


# ==============================
# Bulk Upload Products via CSV
# ==============================
class BulkUploadProductView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']

        try:
            file_data = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(file_data)

            created_products = []
            failed_rows = []

            for row in reader:
                try:
                    category_name = row['category']
                    category, _ = Category.objects.get_or_create(name=category_name)

                    product_data = {
                        'title': row['title'],
                        'product_code': row.get('product_code') or '',
                        'category': category.id,
                        'colors': row.get('colors', []),
                        'available_stock': row['available_stock'],
                        'price': row['price'],
                        'description': row['description'],
                    }

                    serializer = ProductSerializer(data=product_data)
                    if serializer.is_valid():
                        serializer.save()
                        created_products.append(serializer.data)
                    else:
                        failed_rows.append({"row": row, "error": serializer.errors})

                except Exception as e:
                    failed_rows.append({"row": row, "error": str(e)})

            return Response({
                "created_products": created_products,
                "failed_rows": failed_rows,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": f"Error processing file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
