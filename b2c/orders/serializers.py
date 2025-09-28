
from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from b2c.cart.models import CartItem
from b2c.products.models import Products
from b2c.checkout.models import Shipping
from b2c.orders.models import Order, OrderItem, OrderTracking
from b2c.checkout.serializers import ShippingSerializer
from b2c.coupons.models import Coupon
from notifications.models import Notification
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from b2c.products.models import Products
from b2c.checkout.models import Shipping
from b2c.orders.models import Order, OrderItem
from notifications.models import Notification
from b2c.products.models import Products
from b2c.checkout.models import Shipping
from b2c.orders.models import Order, OrderItem, OrderTracking
from notifications.models import Notification
from django.contrib.auth import get_user_model
from .enums import  PaymentMethodChoices


User = get_user_model()



# class OrderItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.CharField(source="product.title", read_only=True)
#     product_image = serializers.ImageField(source="product.image", read_only=True)
#     product_name = serializers.CharField(source="product.title", read_only=True)
#     product_discount = serializers.SerializerMethodField()
#     coupon_discount = serializers.SerializerMethodField()
#     final_price = serializers.SerializerMethodField()  
#     line_total = serializers.SerializerMethodField()

#     class Meta:
#         model = OrderItem
#         fields = [
#             "id", "product", 'product_image',"product_name", "quantity", "price",
#             "product_discount", "coupon_discount", "final_price", "line_total"
#         ]
#         read_only_fields = ["id", "product_name",'product_image', "line_total", "final_price",
#                             "product_discount", "coupon_discount"]

#     def get_product_discount(self, obj):
#         return obj.product.discount if obj.product.discount else 0

#     def get_coupon_discount(self, obj):
#         if obj.coupon:
#             return obj.coupon.discount_percentage
#         return 0

#     def get_final_price(self, obj):
#         # calculate product discounted price
#         product_price = obj.product.price
#         if obj.product.discount:
#             product_price -= product_price * obj.product.discount / 100

#         # apply coupon discount
#         if obj.coupon:
#             product_price -= product_price * obj.coupon.discount_percentage / 100

#         return round(product_price, 2)

#     def get_line_total(self, obj):
#         return round(obj.quantity * self.get_final_price(obj), 2)

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.title", read_only=True)
    product_image = serializers.ImageField(source="product.image", read_only=True)
    product_discount = serializers.SerializerMethodField()
    coupon_discount = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()  
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id", "product", "product_image", "product_name", "quantity", "price",
            "product_discount", "coupon_discount", "final_price", "line_total"
        ]
        read_only_fields = [
            "id", "product_name", "product_image", "line_total", 
            "final_price", "product_discount", "coupon_discount"
        ]

    def get_product_discount(self, obj):
        return obj.product.discount if hasattr(obj.product, "discount") and obj.product.discount else 0

    def get_coupon_discount(self, obj):
        """Get coupon discount percentage from related order if available."""
        if hasattr(obj, "order") and obj.order and getattr(obj.order, "coupon", None):
            return obj.order.coupon.discount_percentage
        return 0

    def get_final_price(self, obj):
        """Calculate final price after product + coupon discount."""
        product_price = obj.product.price

        # Product discount
        if hasattr(obj.product, "discount") and obj.product.discount:
            product_price -= product_price * obj.product.discount / 100

        # Coupon discount (via order)
        if hasattr(obj, "order") and obj.order and getattr(obj.order, "coupon", None):
            product_price -= product_price * obj.order.coupon.discount_percentage / 100

        return round(product_price, 2)

    def get_line_total(self, obj):
        """Total for this line item."""
        return round(obj.quantity * self.get_final_price(obj), 2)




class OrderTrackingSerializer(serializers.ModelSerializer):
    updated_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderTracking
        fields = ['id', 'order', 'status', 'note', 'updated_by', 'created_at']
        read_only_fields = ['updated_by', 'created_at']



class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = ShippingSerializer(read_only=True)
    tracking_history = OrderTrackingSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discounted_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    final_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)  # total after coupon

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'shipping_address',
            'items', 'tracking_history','coupon', 'total_amount', 'discounted_amount','final_amount',
            'is_paid', 'payment_status', 'order_status',
            'stripe_payment_intent', 'stripe_checkout_session_id', 'created_at'
        ]
        read_only_fields = [
            'user', 'order_number', 'items', 'tracking_history',
            'total_amount', 'discounted_amount', 'is_paid',
            'payment_status', 'order_status', 'final_amount','stripe_payment_intent',
            'stripe_checkout_session_id', 'created_at'
        ]




class BuyNowSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)
    payment_method = serializers.ChoiceField(
        choices=[("COD", "Cash on Delivery"), ("ONLINE", "Online Payment")]
    )
    # Shipping details
    full_name = serializers.CharField()
    phone_no = serializers.CharField()
    email = serializers.EmailField()
    street_address = serializers.CharField()
    apartment = serializers.CharField(required=False, allow_blank=True)
    floor = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField()
    zipcode = serializers.CharField()

    def validate_product_id(self, value):
        try:
            Products.objects.get(id=value)
        except Products.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        product = Products.objects.select_for_update().get(id=validated_data["product_id"])
        quantity = validated_data.get("quantity", 1)

        if quantity > product.available_stock:
            raise serializers.ValidationError(f"Only {product.available_stock} items available.")

        # Create shipping address
        shipping = Shipping.objects.create(
            user=user,
            full_name=validated_data["full_name"],
            phone_no=validated_data["phone_no"],
            email=validated_data["email"],
            street_address=validated_data["street_address"],
            apartment=validated_data.get("apartment", ""),
            floor=validated_data.get("floor", ""),
            city=validated_data["city"],
            zipcode=validated_data["zipcode"],
        )

        # Total amount
        total_amount = (
            product.discounted_price * quantity
            if hasattr(product, "discounted_price")
            else product.price * quantity
        )

        # Create order
        order = Order.objects.create(
            user=user,
            shipping_address=shipping,
            total_amount=total_amount,
            payment_status="pending" if validated_data["payment_method"] == "ONLINE" else "cod",
            order_status="PENDING",
            payment_method=validated_data["payment_method"],
        )

        # Create order item
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.discounted_price if hasattr(product, "discounted_price") else product.price,
        )

        # Update stock
        product.available_stock -= quantity
        product.save(update_fields=["available_stock"])

        # Notifications
        Notification.objects.create(
            user=user,
            title="Order Placed",
            message=f"Your order {order.order_number} has been placed successfully.",
        )

        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                title="New Order",
                message=f"New order {order.order_number} placed by {user.email}.",
            )

        return order


