# b2c/products/serializers.py
from rest_framework import serializers
from .models import Category, Product
# b2c/products/serializers.py
from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


# products/serializers.py



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'product_code', 'discount', 'category', 'color', 'available_stock', 'price', 'description']
        read_only_fields = ['product_code']  # product_code is auto-generated

