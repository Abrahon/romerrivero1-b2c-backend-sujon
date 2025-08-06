from rest_framework import serializers
from .models import CartItem
from b2c.products.models import Products

class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'name', 'price']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductInfoSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Products.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'added_at']

        def validate(sel,data):
            product = data.get('product')
            quantity = data.get('quantity')
            if product and quantity:
                if product.stock<quantity:
                    raise serializers.ValidationError(f"only {product.stock} item available in the stock")
                return data
            
            
