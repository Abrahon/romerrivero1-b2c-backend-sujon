from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'product_code', 'category', 'color', 'available_stock', 'price', 'description', 'image']
        read_only_fields = ['product_code']  

    def create(self, validated_data):
        # No seller field anymore, just create the product
        return Product.objects.create(**validated_data)
