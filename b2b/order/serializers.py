from rest_framework import serializers
from .models import Order, OrderItem
from b2b.product.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price_at_time', 'line_total', 'product_title']
        read_only_fields = ['line_total']

    def get_line_total(self, obj):
        return obj.price_at_time * obj.quantity


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'user', 'inquiry', 'items', 'total_amount', 'order_status', 'created_at', 'updated_at']
        read_only_fields = ['order_number', 'user', 'total_amount', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Ensure the user is set to the logged-in user and link to the inquiry
        validated_data['user'] = self.context['request'].user
        order = Order.objects.create(**validated_data)

        # Create the order items based on the provided data
        items_data = self.context['request'].data.get('items', [])
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price_at_time=product.price
            )

        # Calculate the total amount
        total_amount = sum(item['quantity'] * item['price_at_time'] for item in items_data)
        order.total_amount = total_amount
        order.save()

        return order
