from rest_framework import serializers
from .models import WishlistItem
from b2c.products.serializers import ProductSerializer

class WishlistItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'product_details', 'added_at']
        read_only_fields = ['id', 'product_details', 'added_at']
