
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
from .models import Order, OrderStatus
from rest_framework import serializers
from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from b2c.products.models import Products
from b2c.checkout.models import Shipping
from b2c.orders.models import Order, OrderItem
from b2c.coupons.models import Coupon, CouponRedemption
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Order, OrderItem
User = get_user_model()


from rest_framework import serializers
from decimal import Decimal
from .models import OrderItem

from rest_framework import serializers
from decimal import Decimal
from .models import OrderItem
from b2c.products.serializers import ProductSerializer 

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
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
    

    def get_product_image(self, obj):
        request = self.context.get("request")
        
        product = getattr(obj, "product", None)
        if product and hasattr(product, "image") and product.image and request:
            return request.build_absolute_uri(product.image.url)
        
        # fallback if request is not provided or no image exists
        if product and hasattr(product, "image") and product.image:
            return product.image.url

        return None


    def get_product_discount(self, obj):
        return getattr(obj.product, "discount", 0) or 0

    def get_coupon_discount(self, obj):
        coupon = getattr(obj.order, "coupon", None)
        if coupon:
            return coupon.discount_value
            # return order.coupon.discount_value
        return 0
    

    def get_final_price(self, obj):
        price = Decimal(str(obj.product.discounted_price)) 
        coupon = getattr(obj.order, "coupon", None)
        if coupon:
            if coupon.discount_type == "percentage":
                price -= price * Decimal(str(coupon.discount_value)) / Decimal("100")
            else:
                price -= Decimal(str(coupon.discount_value))
        return round(max(price, Decimal("0.00")), 2)

    def get_line_total(self, obj):
        return round(obj.quantity * self.get_final_price(obj), 2)




class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    product = ProductSerializer(read_only=True)
    # product = ProductSerializer(read_only=True)
    shipping_address = ShippingSerializer(read_only=True)
    # tracking_history = OrderTrackingSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discounted_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    final_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True) 

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'product', 'shipping_address',
            'items', 'tracking_history','coupon', 'total_amount', 'discounted_amount','final_amount',
            'is_paid', 'payment_status', 'order_status',
            'stripe_payment_intent', 'stripe_checkout_session_id', 'created_at'
        ]
        read_only_fields = [
            'user', 'order_number', 'items', 'product','tracking_history',
            'total_amount', 'discounted_amount', 'is_paid',
            'payment_status', 'order_status', 'final_amount','stripe_payment_intent',
            'stripe_checkout_session_id', 'created_at'
        ]





class OrderListSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    shipping_address = serializers.CharField(source="shipping_address.address", read_only=True)
    order_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "user_email",
            "order_status",
            "total_amount",
            "created_at",
            "order_items"
        ]

    def get_order_items(self, obj):
        items = obj.orderitem_set.all()
        return [
            {
                "product": i.product.title,
                "quantity": i.quantity,
                "price": float(i.price)
            }
            for i in items
        ]



from rest_framework import serializers
from decimal import Decimal
from .models import OrderTracking, OrderItem
from b2c.orders.serializers import OrderDetailSerializer  # make sure import is correct

class OrderTrackingSerializer(serializers.ModelSerializer):
    updated_by = serializers.StringRelatedField(read_only=True)
    order_items = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()
    items = OrderDetailSerializer(many=True, read_only=True, source='order.items')
    user_email = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField() 

    class Meta:
        model = OrderTracking
        fields = [
            'id', 'order', 'status', 'note', 'updated_by', 'created_at',
            'order_items', 'shipping_address', 'user_email', 'total_amount', 'items'
        ]
        read_only_fields = ['updated_by', 'created_at', 'items', 'total_amount']

    def get_order_items(self, obj):
        items = obj.order.items.all()  # make sure related_name='items'
        return OrderDetailSerializer(items, many=True).data

    def get_shipping_address(self, obj):
        shipping = getattr(obj.order, 'shipping_address', None)
        if shipping:
            return {
                "full_name": shipping.full_name,
                "phone_no": shipping.phone_no,
                "email": shipping.email,
                "street_address": shipping.street_address,
                "apartment": shipping.apartment,
                "floor": shipping.floor,
                "city": shipping.city,
                "zipcode": shipping.zipcode
            }
        return None

    def get_user_email(self, obj):
        return obj.order.user.email if obj.order.user else None

    def get_total_amount(self, obj):
        total = Decimal("0.00")
        for item in obj.order.items.all():
            total += Decimal(item.price) * item.quantity
        return str(total)


class AdminOrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["order_status"]

    def validate_order_status(self, value):
        if value not in OrderStatus.values:
            raise serializers.ValidationError("Invalid order status.")
        return value





class BuyNowSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)
    payment_method = serializers.ChoiceField(choices=[("COD", "Cash on Delivery"), ("ONLINE", "Online Payment")])
    shipping_id = serializers.IntegerField(required=False)
    coupon_code = serializers.CharField(required=False, allow_blank=True)

    # Shipping fields if no shipping_id is provided
    full_name = serializers.CharField(required=False)
    phone_no = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    street_address = serializers.CharField(required=False)
    apartment = serializers.CharField(required=False, allow_blank=True)
    floor = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False)
    zipcode = serializers.CharField(required=False)

    def validate_product_id(self, value):
        if not Products.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exist.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        product = Products.objects.select_for_update().get(id=validated_data["product_id"])
        quantity = validated_data.get("quantity", 1)

        # Step 0: Validate stock
        if quantity > product.available_stock:
            raise serializers.ValidationError(f"Only {product.available_stock} items available.")

        # Step 1: Handle shipping
        shipping_id = validated_data.get("shipping_id")
        if shipping_id:
            shipping = get_object_or_404(Shipping, id=shipping_id, user=user)
        else:
            shipping = Shipping.objects.create(
                user=user,
                full_name=validated_data.get("full_name", ""),
                phone_no=validated_data.get("phone_no", ""),
                email=validated_data.get("email", ""),
                street_address=validated_data.get("street_address", ""),
                apartment=validated_data.get("apartment", ""),
                floor=validated_data.get("floor", ""),
                city=validated_data.get("city", ""),
                zipcode=validated_data.get("zipcode", ""),
            )

        # Step 2: Determine product price
        product_price = getattr(product, "discounted_price", None)
        if product_price is None:
            product_price = product.price

        total_amount = Decimal(product.price) * quantity          # original price total
        discounted_amount = Decimal(product_price) * quantity    # price with product discount
        final_amount = discounted_amount                          # before coupon

        # Step 3: Apply coupon if provided
        coupon_code = validated_data.get("coupon_code")
        coupon = None
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True)
                now = timezone.now()
                if coupon.valid_from and coupon.valid_from > now:
                    raise serializers.ValidationError("Coupon is not yet valid.")
                if coupon.valid_to and coupon.valid_to < now:
                    raise serializers.ValidationError("Coupon has expired.")

                # Coupon base amount logic
                base_amount_for_coupon = discounted_amount if getattr(product, "discounted_price", None) else total_amount

                if coupon.discount_type == "percentage":
                    discount_amount = (base_amount_for_coupon * Decimal(coupon.discount_value)) / Decimal("100")
                else:
                    discount_amount = Decimal(coupon.discount_value)

                final_amount = base_amount_for_coupon - discount_amount
                final_amount = max(final_amount, Decimal("0.00"))

                # Record coupon redemption
                CouponRedemption.objects.get_or_create(coupon=coupon, user=user)

            except Coupon.DoesNotExist:
                raise serializers.ValidationError("Invalid coupon code.")

        if final_amount <= 0:
            raise serializers.ValidationError("Final amount is zero or negative. Cannot proceed to checkout.")

        # Step 4: Create order
        order = Order.objects.create(
            user=user,
            shipping_address=shipping,
            total_amount=total_amount,
            discounted_amount=discounted_amount,
            final_amount=final_amount,
            payment_method=validated_data["payment_method"],
            
            # ✅ Fix payment + order statuses
            payment_status="pending" if validated_data["payment_method"] == "ONLINE" else "success",
            order_status="PENDING" if validated_data["payment_method"] == "ONLINE" else "PROCESSING",
            
            coupon=coupon
        )


        # Step 5: Create OrderItem
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product_price,
        )

        # Step 6: Reduce stock
        product.available_stock -= quantity
        product.save(update_fields=["available_stock"])

        # Step 7: Notifications
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
