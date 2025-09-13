from rest_framework import serializers
from .models import Shipping
from b2c.orders.models import Order

class ShippingSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        source='order',
        write_only=True,
        required=False  # optional if shipping is created before order
    )

    class Meta:
        model = Shipping
        fields = [
            'id', 'user', 'full_name', 'phone_no', 'email', 'street_address',
            'apartment', 'floor', 'city', 'zipcode', 'order_id', 'order', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'order', 'status', 'created_at', 'updated_at']

    def validate_phone_no(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        return value

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value

    def validate(self, data):
        required_fields = ['full_name', 'street_address', 'city', 'zipcode']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: f"{field.replace('_',' ').capitalize()} is required."})
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        # Remove 'user' from validated_data if it exists to avoid duplicates
        validated_data.pop('user', None)
        return Shipping.objects.create(user=user, **validated_data)
