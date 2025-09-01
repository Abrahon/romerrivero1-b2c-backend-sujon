from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
import csv
from django.conf import settings
from .models import Product
from .serializers import ProductSerializer
from django.core.exceptions import ValidationError
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Category
from .serializers import CategorySerializer
from rest_framework.parsers import MultiPartParser, FormParser

# ==============================
# Admin Views (CRUD for Category)
# ==============================
class AdminCategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()


class AdminCategoryUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, *args, **kwargs):
        try:
            category = self.get_object()
            category.delete()
            return Response({"message": "Category deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({"message": "Category not found."}, status=status.HTTP_404_NOT_FOUND)


# ==============================
# Public Views (Users)
# ==============================
class CategoryListView(generics.ListAPIView):
    """
    List all categories (for users).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class CategoryDetailView(generics.RetrieveAPIView):
    """
    Get details of a specific category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


# Admin Views - List, Create, Update and Delete
class AdminProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (MultiPartParser, FormParser) 

    def perform_create(self, serializer):
        try:
            # Save the product
            serializer.save()
        except ValidationError as e:
            # Handle validation errors
            return Response({"detail": f"Validation Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# Admin Views - Update and Delete a Product
class AdminProductCreateUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def update(self, request, *args, **kwargs):
        try:
            # Get the product to update
            product = self.get_object()
            
            # Update the product with the new data from the request
            serializer = self.get_serializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        
        
    def delete(self, request, *args, **kwargs):
        try:
            product = self.get_object()  
            product.delete()  
            return Response({"message": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({"message": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        

# User Views - List Products and Filter by Category
class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="category", lookup_expr="iexact")

    class Meta:
        model = Product
        fields = ["category"]

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


# Product Detail View for User
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  

# Bulk Upload Products via CSV
class BulkUploadProductView(APIView):
    """
    Bulk upload products via CSV.
    """
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
                    category, created = Category.objects.get_or_create(name=category_name)

                    product_data = {
                        'title': row['title'],
                        'product_code': row['product_code'],
                        'category': category,
                        'color': row['color'],
                        'available_stock': row['available_stock'],
                        'price': row['price'],
                        'description': row['description'],
                    }

                    product_serializer = ProductSerializer(data=product_data)
                    if product_serializer.is_valid():
                        product_serializer.save()
                        created_products.append(product_serializer.data)
                    else:
                        failed_rows.append({"row": row, "error": product_serializer.errors})
                except Exception as e:
                    failed_rows.append({"row": row, "error": str(e)})

            return Response({
                "created_products": created_products,
                "failed_rows": failed_rows,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": f"Error processing file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    permission_classes = [AllowAny]  # Allow anyone to upload products

