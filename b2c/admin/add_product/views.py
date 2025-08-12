from django.shortcuts import render
# Create your views here.
# b2c/products/views.py
from rest_framework import generics
# from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
# b2c/products/views.py
from rest_framework import generics
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
import csv, os
from django.conf import settings
from django.core.files import File
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# Category APIs
class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

# Product APIs
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
  
  
#bulk upload APIs(like csv)


class BulkUploadProductView(APIView):
    """
    Bulk upload products via CSV.
    """
    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        
        try:
            # Reading the uploaded CSV file
            file_data = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(file_data)

            created_products = []
            failed_rows = []

            for row in reader:
                try:
                    # Extract category or create it
                    category_name = row['category']
                    category, created = Category.objects.get_or_create(name=category_name)

                    # Prepare product data
                    product_data = {
                        'title': row['title'],
                        'product_code': row['product_code'],
                        'discount': row['discount'],
                        'category': category,
                        'color': row['color'],
                        'available_stock': row['available_stock'],
                        'price': row['price'],
                        'description': row['description']
                    }

                    # Validate and save the product using the serializer
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
    
    permission_classes = [AllowAny]