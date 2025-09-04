from rest_framework import serializers
from b2b.order.models import Order
from b2b.product.models import Product

# Top Selling Products
class TopSellingProductsSerializer(serializers.ModelSerializer):
    total_sales = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Product
        fields = ['id', 'title', 'total_sales']
