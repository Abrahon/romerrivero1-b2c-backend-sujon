from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils.text import slugify
import csv
import uuid
import logging
import django_filters

from .models import Products, ProductCategory
from .serializers import ProductSerializer, CategorySerializer
from .enums import ProductStatus

logger = logging.getLogger(__name__)

# -------------------------
# ===== ADMIN VIEWS =====
# -------------------------

class AdminCategoryListCreateView(generics.ListCreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]



class AdminCategoryProductListView(generics.ListAPIView):
    """
    Admin: List products of a category
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        category_id = self.kwargs.get("category_id")
        print(category_id.id)
        return Products.objects.filter(category_id=category_id)


class AdminProductListCreateView(generics.ListCreateAPIView):
    """
    Admin: List all products and create product
    """
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'status']

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            
            # Discount handling
            discount = data.get("discount", 0)
            try:
                discount = float(discount)
                if discount < 0 or discount > 100:
                    return Response({"error": "Discount must be between 0 and 100."},
                                    status=status.HTTP_400_BAD_REQUEST)
                data["discount"] = discount
            except ValueError:
                return Response({"error": "Discount must be a number."},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "message": "✅ Product added successfully!",
                "product": serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminProductRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin: Retrieve, update or delete product
    """
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response({
                "message": "✅ Product updated successfully!",
                "product": response.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        product_title = instance.title
        self.perform_destroy(instance)
        return Response({
            "message": f"🗑️ Product '{product_title}' deleted successfully!"
        }, status=status.HTTP_200_OK)


class AdminProductBulkDelete(APIView):
    """
    Admin: Bulk delete products by IDs
    """
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, *args, **kwargs):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"error": "No product IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = Products.objects.filter(id__in=ids).delete()
        return Response({
            "message": f"🗑️ {deleted_count} products deleted successfully"
        }, status=status.HTTP_200_OK)

    """
    Admin: Bulk delete products by IDs
    """
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, *args, **kwargs):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"error": "No product IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = Products.objects.filter(id__in=ids).delete()
        return Response({"message": f"{deleted_count} products deleted successfully"}, status=status.HTTP_200_OK)



class AdminProductStatusListView(generics.ListAPIView):
    """
    Admin: Filter products by status
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        status_param = self.request.query_params.get("status", "").strip().lower()
        if status_param == "active":
            return Products.objects.filter(status=ProductStatus.ACTIVE)
        elif status_param == "inactive":
            return Products.objects.filter(status=ProductStatus.INACTIVE)
        return Products.objects.none()


class AdminBulkUploadProductView(APIView):
    """
    Admin: Bulk upload products from CSV
    """
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if 'file' not in request.FILES:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']

        try:
            file_data = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(file_data)
        except Exception as e:
            logger.error(f"CSV read error: {str(e)}")
            return Response({"detail": f"Error reading CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        created_products = []
        failed_rows = []

        for row in reader:
            try:
                # Category
                category_name = row.get('category')
                if not category_name:
                    raise ValueError("Category is missing.")
                category, _ = ProductCategory.objects.get_or_create(name=category_name)

                # Colors
                colors = [c.strip() for c in row.get('colors', '').split(',') if c.strip()]

                # Discount
                discount = row.get('discount', 0)
                try:
                    discount = float(discount)
                    if discount < 0 or discount > 100:
                        discount = 0
                except ValueError:
                    discount = 0

                product_data = {
                    'title': row.get('title'),
                    'product_code': row.get('product_code', ''),
                    'category': category.id,
                    'colors': colors,
                    'available_stock': row.get('available_stock', 0),
                    'price': row.get('price', 0),
                    'description': row.get('description', ''),
                    'discount': discount,
                    'status': row.get('status', ProductStatus.INACTIVE),
                }

                serializer = ProductSerializer(data=product_data)
                if serializer.is_valid():
                    serializer.save()
                    created_products.append(serializer.data)
                else:
                    failed_rows.append({"row": row, "errors": serializer.errors})

            except Exception as e:
                failed_rows.append({"row": row, "errors": str(e)})
                logger.error(f"Error processing row {row}: {str(e)}")

        return Response({
            "created_products": created_products,
            "failed_rows": failed_rows
        }, status=status.HTTP_201_CREATED)


# -------------------------
# ===== AUTHENTICATED USER VIEWS =====
# -------------------------

class UserCategoryListView(generics.ListAPIView):
    """
    Authenticated user: list categories
    """
    queryset = ProductCategory.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class UserCategoryProductListView(generics.ListAPIView):
    """
    Authenticated user: list active products in a category
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        category_id = self.kwargs.get("category_id")
        return Products.objects.filter(category_id=category_id, status=ProductStatus.ACTIVE)


class UserProductListView(generics.ListAPIView):
    """
    Authenticated user: list all active products
    """
    queryset = Products.objects.filter(status=ProductStatus.ACTIVE)
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']


class UserProductDetailView(generics.RetrieveAPIView):
    """
    Authenticated user: get single active product details
    """
    queryset = Products.objects.filter(status=ProductStatus.ACTIVE)
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "id"


class UserProductSearchView(generics.ListAPIView):
    """
    Authenticated user: search/filter active products
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get("q", "")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        products = Products.objects.filter(status=ProductStatus.ACTIVE)

        if query:
            products = products.filter(Q(title__icontains=query) | Q(description__icontains=query))

        if min_price:
            try:
                min_price_val = float(min_price)
                products = products.filter(price__gte=min_price_val)
            except ValueError:
                pass

        if max_price:
            try:
                max_price_val = float(max_price)
                products = products.filter(price__lte=max_price_val)
            except ValueError:
                pass

        return products
