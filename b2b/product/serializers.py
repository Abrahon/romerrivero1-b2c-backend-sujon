# b2c/products/serializers.py
from rest_framework import serializers
from .models import Product, Category
from django.contrib.auth import get_user_model

User = get_user_model() 

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)  

    class Meta:
        model = Product
        fields = ['id', 'title', 'product_code', 'category', 'category_name', 'color', 'available_stock', 'price', 'description' 'image']
        read_only_fields = ['product_code', 'seller_name', 'category_name']

    def create(self, validated_data):
        """Override create method to set the seller as the current user (admin)"""
        return Product.objects.create(seller=self.context['request'].user, **validated_data)


