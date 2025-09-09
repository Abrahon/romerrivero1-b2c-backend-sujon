from rest_framework import serializers
from b2b.product.models import Product
from .models import Inquiry, AdminNotification
from django.contrib.auth import get_user_model

User = get_user_model()


class InquirySerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = Inquiry
        fields = ['id', 'user', 'product', 'quantity', 'subject', 'message', 'price_at_inquiry', 'is_resolved', 'created_at', 'updated_at']
        read_only_fields = ['user', 'price_at_inquiry', 'created_at', 'updated_at']

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity')
        if product and quantity and product.available_stock < quantity:
            raise serializers.ValidationError(f"Only {product.available_stock} items are available in stock.")
        return data


class AdminNotificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = AdminNotification
        fields = ['id', 'user', 'message', 'reply','is_read', 'created_at']
        read_only_fields = ['message','reply','created_at']
