from rest_framework import serializers
from .models import Inquiry, AdminNotification
from b2b.product.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

class InquirySerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())  # Ensures product exists
    quantity = serializers.IntegerField(min_value=1)  

    class Meta:
        model = Inquiry
        fields = ['id', 'user', 'product', 'quantity', 'subject', 'message', 'is_resolved', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity')
        if product and quantity:
            if product.available_stock < quantity:
                raise serializers.ValidationError(f"Only {product.available_stock} items are available in stock.")
        return data


class AdminNotificationSerializer(serializers.ModelSerializer):
    # optional if you want to expose user in serializer
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = AdminNotification
        fields = ['id', 'user', 'message', 'is_read', 'created_at']
        read_only_fields = ['message', 'created_at']
