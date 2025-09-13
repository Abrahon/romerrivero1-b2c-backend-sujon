# b2c/serializers.py
from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from b2c.cart.models import CartItem
from b2c.products.models import Products
from b2c.checkout.models import Shipping
from b2c.orders.models import Order, OrderItem, OrderTracking
from b2c.products.serializers import ProductSerializer
from b2c.checkout.serializers import ShippingSerializer


# ---------------------- ORDER ITEM ----------------------

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price", "line_total"]
        read_only_fields = ["id", "product_name", "line_total"]


# ---------------------- ORDER TRACKING ----------------------
class OrderTrackingSerializer(serializers.ModelSerializer):
    updated_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderTracking
        fields = ['id', 'order', 'status', 'note', 'updated_by', 'created_at']
        read_only_fields = ['updated_by', 'created_at']

    def validate(self, data):
        order = data.get('order')
        if not order:
            raise serializers.ValidationError({"order": "Order is required."})
        if data.get('status') not in dict(order.order_status.field.choices):
            raise serializers.ValidationError({"status": "Invalid status."})
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['updated_by'] = user
        tracking = OrderTracking.objects.create(**validated_data)
        # Optional: update order status automatically
        order = tracking.order
        order.order_status = tracking.status
        order.save()
        return tracking


# ---------------------- ORDER ----------------------
class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = ShippingSerializer(read_only=True)
    tracking_history = OrderTrackingSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'shipping_address',
            'items', 'tracking_history', 'total_amount', 'is_paid',
            'payment_status', 'order_status', 'stripe_payment_intent',
            'stripe_checkout_session_id', 'created_at',
          
        ]
        read_only_fields = [
            'user', 'order_number', 'items', 'tracking_history',
            'total_amount', 'is_paid', 'payment_status', 'order_status',
            'stripe_payment_intent', 'stripe_checkout_session_id', 'created_at'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        from b2c.cart.models import CartItem

        cart_items = CartItem.objects.filter(user=user).select_related('product')
        if not cart_items.exists():
            raise serializers.ValidationError({"detail": "Cart is empty."})

        shipping = Shipping.objects.filter(user=user).last()
        if not shipping:
            raise serializers.ValidationError({"detail": "Shipping information missing."})

        total_amount = Decimal("0.00")

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                shipping_address=f"{shipping.full_name}, {shipping.street_address}, {shipping.city}, {shipping.zipcode}"
            )

            for item in cart_items:
                if item.quantity > item.product.available_stock:
                    raise serializers.ValidationError({
                        "quantity": f"Only {item.product.available_stock} items available for {item.product.title}."
                    })

                price = item.product.discounted_price
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price_at_time=price
                )

                # Reduce stock
                item.product.available_stock -= item.quantity
                item.product.save(update_fields=['available_stock'])
                total_amount += price * item.quantity

            order.total_amount = total_amount
            order.save(update_fields=['total_amount'])

            # Clear cart
            cart_items.delete()

        return order
    

# class OrderDetailSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True, read_only=True)
#     shipping_address = ShippingSerializer(read_only=True)
#     tracking_history = OrderTrackingSerializer(many=True, read_only=True)

#     class Meta:
#         model = Order
#         fields = [
#             'id', 'order_number', 'user', 'shipping_address',
#             'items', 'tracking_history', 'total_amount', 'is_paid',
#             'payment_status', 'order_status', 'stripe_payment_intent',
#             'stripe_checkout_session_id', 'created_at'
#         ]
#         read_only_fields = fields

#     def create(self, validated_data):
#         user = self.context['request'].user
#         from b2c.cart.models import CartItem
#         from b2c.checkout.models import Shipping

#         cart_items = CartItem.objects.filter(user=user).select_related('product')
#         if not cart_items.exists():
#             raise serializers.ValidationError({"detail": "Cart is empty."})

#         shipping = Shipping.objects.filter(user=user).last()
#         if not shipping:
#             raise serializers.ValidationError({"detail": "Shipping information missing."})

#         # ✅ Add your provided code here
#         with transaction.atomic():
#             # 1️⃣ Create the order
#             order = Order.objects.create(
#                 user=user,
#                 shipping_address=shipping
#             )

#             # 2️⃣ Add initial tracking entry
#             OrderTracking.objects.create(
#                 order=order,
#                 status="PENDING",
#                 note="Order has been placed.",
#                 updated_by=user
#             )

#             # 3️⃣ Create OrderItems from cart
#             for item in cart_items:
#                 if item.quantity > item.product.available_stock:
#                     raise serializers.ValidationError({
#                         "quantity": f"Only {item.product.available_stock} items available for {item.product.title}."
#                     })

#                 price = item.product.discounted_price
#                 OrderItem.objects.create(
#                     order=order,
#                     product=item.product,
#                     quantity=item.quantity,
#                     price=price
#                 )

#                 # Reduce stock
#                 item.product.available_stock -= item.quantity
#                 item.product.save(update_fields=['available_stock'])

#             # 4️⃣ Update total amount
#             total_amount = sum(item.product.discounted_price * item.quantity for item in cart_items)
#             order.total_amount = total_amount
#             order.save(update_fields=['total_amount'])

#             # 5️⃣ Clear cart
#             cart_items.delete()

#         return order
