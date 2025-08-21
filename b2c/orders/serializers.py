# b2c/orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem
# from b2c.products.serializers import ProductListSerializer  # optional: reuse your product serializer

# Minimal product info serializer to avoid overfetching
class OrderProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="product.id", read_only=True)
    name = serializers.CharField(source="product.name", read_only=True)
    price = serializers.DecimalField(source="product.price", max_digits=12, decimal_places=2, read_only=True)


class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderProductSerializer(read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price_at_time", "line_total"]

    def get_line_total(self, obj):
        return obj.line_total


class OrderListSerializer(serializers.ModelSerializer):
    """Used for order list (summary) - keeps payload light"""
    items_count = serializers.IntegerField(source="items.count", read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    order_status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "order_number", "created_at", "total_amount", "order_status", "items_count"]


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "created_at",
            "shipping_address",
            "total_amount",
            "is_paid",
            "payment_status",
            "order_status",
            "stripe_payment_intent",
            "stripe_checkout_session_id",
            "items",
        ]
        read_only_fields = ["order_number", "created_at", "total_amount", "items"]




class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "user",
            "shipping_address",
            "total_amount",
            "is_paid",
            "payment_status",
            "order_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
