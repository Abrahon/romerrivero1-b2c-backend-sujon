from django.shortcuts import render
from rest_framework import generics
from .models import Category,Products
from .serializers import CategorySerializer,ProductSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated


# Create your views here.
class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


# product created list
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'  

    def get_object(self):
        """
        Customizing the object retrieval (optional).
        You can add custom logic here if needed before returning the object.
        """
        obj = super().get_object()
        # Optional: Add custom logging, validation, or preprocessing here
        return obj



