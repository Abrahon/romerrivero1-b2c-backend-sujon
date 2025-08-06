from rest_framework import serializers
from .models import Order,OrderItem



class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price_at_time']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True) 

    class Meta:
        model = Order
        fields = ['id', 'user', 'shipping_address', 'created_at', 'is_paid', 'payment_status', 'items']
    

