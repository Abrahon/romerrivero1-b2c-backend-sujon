# b2c/products/serializers.py
from rest_framework import serializers
from .models import Category, Product
# b2c/products/serializers.py
from rest_framework import serializers
from .models import Product, Category,Wishlist

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'product_code', 'discount', 'category', 'color', 'available_stock', 'price', 'description']
        read_only_fields = ['product_code'] 


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "product", "added_at"]