from rest_framework import serializers
from .models import Category,Products

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','slug','description']



class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Products
        fields = [
            'id', 'title', 'slug', 'description',
            'price', 'stock_quantity', 'image',
            'is_active', 'rating', 'tags',
            'category', 'category_id'
        ]