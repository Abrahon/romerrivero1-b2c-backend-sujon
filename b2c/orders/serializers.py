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
from b2c.coupons.models import Coupon
from b2c.cart.models import CartItem
from b2c.checkout.models import Shipping
from notifications.models import Notification
from accounts.models import User 
from b2c.coupons.models import Coupon  # Your coupon model

# # ---------------------- ORDER ITEM ----------------------

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
    
# ---------------------- ORDER DETAIL ----------------------

class OrderDetailSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    shipping_address = ShippingSerializer(read_only=True)
    tracking_history = serializers.SerializerMethodField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discounted_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'shipping_address',
            'items', 'tracking_history', 'total_amount', 'discounted_amount',
            'is_paid', 'payment_status', 'order_status',
            'stripe_payment_intent', 'stripe_checkout_session_id', 'created_at'
        ]
        read_only_fields = [
            'user', 'order_number', 'items', 'tracking_history',
            'total_amount', 'discounted_amount', 'is_paid',
            'payment_status', 'order_status', 'stripe_payment_intent',
            'stripe_checkout_session_id', 'created_at'
        ]

    def get_items(self, obj):
        return [
            {
                "product_id": item.product.id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price": item.price,
                "line_total": item.line_total
            } for item in obj.items.all()
        ]

    def get_tracking_history(self, obj):
        return [
            {
                "status": t.status,
                "note": t.note,
                "updated_by": str(t.updated_by) if t.updated_by else None,
                "created_at": t.created_at
            } for t in obj.tracking_history.all()
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        cart_items = CartItem.objects.filter(user=user).select_related('product')
        if not cart_items.exists():
            raise serializers.ValidationError({"detail": "Cart is empty."})

        shipping = Shipping.objects.filter(user=user).last()
        if not shipping:
            raise serializers.ValidationError({"detail": "Shipping information missing."})

        # Check if a coupon is applied in the context
        coupon_code = self.context.get('coupon_code')
        coupon = None
        discount_amount = Decimal("0.00")
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True)
            except Coupon.DoesNotExist:
                raise serializers.ValidationError({"coupon": "Invalid or inactive coupon code."})

        total_amount = Decimal("0.00")

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                shipping_address=f"{shipping.full_name}, {shipping.street_address}, {shipping.city}, {shipping.zipcode}"
            )

            for item in cart_items:
                if item.quantity > item.product.available_stock:
                    raise serializers.ValidationError({
                        "quantity": f"Only {item.product.available_stock} items available for {item.product.name}."
                    })

                price = item.product.discounted_price
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=price
                )

                item.product.available_stock -= item.quantity
                item.product.save(update_fields=['available_stock'])
                total_amount += price * item.quantity

            # Apply coupon if available
            discounted_amount = total_amount
            if coupon:
                if coupon.discount_type == 'PERCENT':
                    discount_amount = (total_amount * coupon.discount_value) / 100
                elif coupon.discount_type == 'FLAT':
                    discount_amount = coupon.discount_value
                discounted_amount = max(total_amount - discount_amount, Decimal("0.00"))
                coupon.used += 1
                coupon.save(update_fields=['used'])

            order.total_amount = total_amount
            order.save(update_fields=['total_amount'])

            # Clear cart
            cart_items.delete()

            # ----------------- ADD NOTIFICATIONS -----------------
            # Notify the customer
            Notification.objects.create(
                user=user,
                type="ORDER",
                message=f"Your order {order.order_number} has been placed successfully."
            )

            # Notify all admins
            admins = User.objects.filter(is_staff=True)
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    type="ORDER",
                    message=f"New order {order.order_number} placed by {user.email}."
                )
            # ------------------------------------------------------

        return order


# class OrderDetailSerializer(serializers.ModelSerializer):
#     ...
#     coupon_code = serializers.CharField(write_only=True, required=False)

#     class Meta:
#         model = Order
#         fields = [
#             'id', 'order_number', 'user', 'shipping_address',
#             'items', 'tracking_history', 'total_amount', 'discount_amount',
#             'final_amount', 'coupon_code', 'is_paid', 'payment_status',
#             'order_status', 'stripe_payment_intent',
#             'stripe_checkout_session_id', 'created_at'
#         ]
#         read_only_fields = [
#             'user', 'order_number', 'items', 'tracking_history',
#             'total_amount', 'discount_amount', 'final_amount',
#             'is_paid', 'payment_status', 'order_status',
#             'stripe_payment_intent', 'stripe_checkout_session_id', 'created_at'
#         ]

#     def create(self, validated_data):
#         user = self.context['request'].user
#         coupon_code = validated_data.pop("coupon_code", None)

       

#         cart_items = CartItem.objects.filter(user=user).select_related('product')
#         if not cart_items.exists():
#             raise serializers.ValidationError({"detail": "Cart is empty."})

#         shipping = Shipping.objects.filter(user=user).last()
#         if not shipping:
#             raise serializers.ValidationError({"detail": "Shipping information missing."})

#         total_amount = Decimal("0.00")
#         discount_amount = Decimal("0.00")
#         coupon = None

#         with transaction.atomic():
#             order = Order.objects.create(
#                 user=user,
#                 shipping_address=shipping
#             )

#             # Create Order Items
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

#                 item.product.available_stock -= item.quantity
#                 item.product.save(update_fields=['available_stock'])
#                 total_amount += price * item.quantity

#             # ✅ Apply Coupon if Provided
#             if coupon_code:
#                 try:
#                     coupon = Coupon.objects.get(code=coupon_code)
#                     if not coupon.is_valid():
#                         raise serializers.ValidationError({"coupon": "Coupon is invalid or expired."})

#                     if coupon.discount_type == "percent":
#                         discount_amount = (total_amount * coupon.discount_value) / Decimal("100")
#                     else:
#                         discount_amount = coupon.discount_value

#                     # Ensure discount doesn’t exceed total
#                     discount_amount = min(discount_amount, total_amount)

#                     coupon.used_count += 1
#                     coupon.save(update_fields=["used_count"])
#                 except Coupon.DoesNotExist:
#                     raise serializers.ValidationError({"coupon": "Invalid coupon code."})

#             # Finalize Order
#             order.total_amount = total_amount
#             order.discount_amount = discount_amount
#             order.final_amount = total_amount - discount_amount
#             order.coupon = coupon
#             order.save(update_fields=['total_amount', 'discount_amount', 'final_amount', 'coupon'])

#             # Clear Cart
#             cart_items.delete()

#         return order
