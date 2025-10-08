

from rest_framework import serializers
from .models import Shipping
from b2c.orders.models import Order

class ShippingSerializer(serializers.ModelSerializer):
    shipping_id = serializers.IntegerField(source='id', read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        source='order',
        write_only=True,
        required=False  # allow shipping creation before order
    )

    class Meta:
        model = Shipping
        fields = [
            'shipping_id', 'user', 'full_name', 'phone_no', 'email', 'street_address',
            'apartment', 'floor', 'city', 'zipcode', 'order_id', 'order', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'order', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data.pop('user', None) 
        return Shipping.objects.create(user=user, **validated_data)
