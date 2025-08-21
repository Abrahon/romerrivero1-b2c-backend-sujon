from rest_framework import generics, permissions
from .models import Product
from .serializers import ProductSerializer
import csv, os
from django.conf import settings
from django.core.files import File
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework import generics
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


# Admin Views Read,write,update and delete
class AdminProductCreateUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # Only admin can create, update or delete products.
    permission_classes = [permissions.IsAdminUser]  

    def perform_create(self, serializer):
        
        serializer.save(seller=self.request.user)


# User Views (Product List and Details)
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    # Anyone can view products
    permission_classes = [permissions.AllowAny]  

    def get_queryset(self):
        """Allow filtering by category"""
        queryset = Product.objects.all()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__name=category)
        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # Anyone can view product details
    permission_classes = [permissions.AllowAny] 
    

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

   

