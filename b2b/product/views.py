from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework import generics, permissions, status, filters as drf_filters
import csv
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
import csv, uuid, requests
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import uuid
import requests
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Product, Category
from .serializers import ProductSerializer
from .enums import ProductStatus
from .serializers import ProductSerializer, CategorySerializer
from rest_framework import status as drf_status


# Admin Views CRUD for Category
class AdminCategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]



# Admin Views - CRUD for Product
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

# ststus views
class StatusProductAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        status_param = request.query_params.get('status', None)
        
        if  status_param:
            status_param = status_param.lower()
            if status_param not in ['active','inactive']:
                return Response(
                    {"error": "Invalid status. Use 'active' or 'inactive'."},
                    status=drf_status.HTTP_400_BAD_REQUEST
                )
            products = Product.objects.filter(status=status_param)
        else:
            products = Product.objects.all()
        serializer = ProductSerializer(products,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
        

# Admin Views - Bulk Delete Products
class AdminProductBulkDelete(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, *args, **kwargs):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"error": "No product IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count, _ = Product.objects.filter(id__in=ids).delete()
        return Response({"message": f"{deleted_count} products deleted successfully"}, status=status.HTTP_200_OK)


# User Views

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category__id", lookup_expr="exact")

    class Meta:
        model = Product
        fields = ["category"]


class ProductSearchFilterView(APIView):
    def get(self, request):
        query = request.query_params.get("q", None)   
        category = request.query_params.get("category", None)  
        min_price = request.query_params.get("min_price", None)  #
        max_price = request.query_params.get("max_price", None)

        products = Product.objects.all()

        # Search by title or description
        if query:
            products = products.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )

        # Filter by category
        if category:
            products = products.filter(category__icontains=category)

        # Filter by price range
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        # Error handling: no products found
        if not products.exists():
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        """
        CSV format:
        title,product_code,category,colors,available_stock,price,description,images
        "Pen A","123","Stationery","Red,Blue","50","99.00","Nice pen","https://example.com/pen-a-1.jpg|https://example.com/pen-a-2.jpg"
        """
        if 'file' not in request.FILES:
            return Response({"detail": "No file provided."}, status=400)

        file = request.FILES['file']

        try:
            file_data = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(file_data)

            created_products = []
            failed_rows = []

            for row in reader:
                try:
                    # --- Handle Category ---
                    category_name = row['category']
                    category, _ = Category.objects.get_or_create(name=category_name)

                    # --- Handle Colors ---
                    colors = row.get('colors', '')
                    if colors:
                        if isinstance(colors, str):
                            colors = [c.strip() for c in colors.split(',')]
                    else:
                        colors = []

                    # --- Handle Images ---
                    images_str = row.get('images', '')
                    image_paths = []
                    if images_str:
                        urls = [u.strip() for u in images_str.split('|') if u.strip()]
                        for url in urls:
                            try:
                                response = requests.get(url)
                                if response.status_code == 200:
                                    ext = url.split('.')[-1]
                                    seo_name = f"{slugify(row['title'])}-{uuid.uuid4().hex}.{ext}"
                                    full_path = f'product_images/{seo_name}'
                                    default_storage.save(full_path, ContentFile(response.content))
                                    image_paths.append(full_path)
                            except Exception as e:
                                failed_rows.append({"row": row, "error": f"Image download failed: {str(e)}"})

                    # --- Prepare Product Data ---
                    product_data = {
                        'title': row['title'],
                        'product_code': row.get('product_code') or '',
                        'category': category.id,
                        'colors': colors,
                        'available_stock': row['available_stock'],
                        'price': row['price'],
                        'description': row['description'],
                        'images': image_paths
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
            }, status=201)

        except Exception as e:
            return Response({"detail": f"Error processing file: {str(e)}"}, status=400)
