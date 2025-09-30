from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework import generics, permissions
from .serializers import OrderTrackingSerializer
# Models
from b2c.cart.models import CartItem
from b2c.checkout.models import Shipping
from b2c.products.models import Products
from b2c.orders.models import Order, OrderItem, OrderTracking
from notifications.models import Notification
# Serializers
from b2c.orders.serializers import (
    OrderItemSerializer,
    OrderDetailSerializer,
    OrderTrackingSerializer,
    BuyNowSerializer,  
)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["order_status", "payment_status"]
    search_fields = ["order_number", "items__product__title"]
    ordering_fields = ["created_at", "total_amount"]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("shipping_address").prefetch_related("items__product").order_by("-created_at")


from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from b2c.orders.models import Order, OrderItem, OrderTracking
from b2c.cart.models import CartItem
from b2c.coupons.models import Coupon, CouponRedemption

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, filters
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from b2c.orders.models import Order, OrderItem, OrderTracking
from b2c.cart.models import CartItem
from b2c.coupons.models import Coupon, CouponRedemption
from b2c.checkout.models import Shipping

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from decimal import Decimal
from .models import Order, OrderItem, OrderTracking
from b2c.products.models import Products
from b2c.checkout.models import Shipping
from b2c.coupons.models import Coupon, CouponRedemption

from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# from .models import CartItem, Order, OrderItem, Shipping, Coupon, CouponRedemption
# from .models import 

class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        shipping_id = request.data.get("shipping_id")
        cart_item_ids = request.data.get("cart_item_ids", [])
        coupon_code = request.data.get("coupon_code")

        if not shipping_id or not cart_item_ids:
            return Response({"error": "shipping_id and cart_item_ids are required"}, status=400)

        shipping = get_object_or_404(Shipping, id=shipping_id, user=user)
        cart_items = CartItem.objects.filter(user=user, id__in=cart_item_ids).select_related("product")
        if not cart_items.exists():
            return Response({"error": "Selected cart items not found"}, status=400)

        order = Order.objects.create(
            user=user,
            shipping_address=shipping,
            total_amount=Decimal("0.00"),
            discounted_amount=Decimal("0.00"),
            final_amount=Decimal("0.00"),
            payment_status="pending",
            order_status="PENDING",
        )

        total_amount = Decimal("0.00")
        discounted_amount = Decimal("0.00")
        final_amount = Decimal("0.00")

        # First, calculate total_amount and discounted_amount per product
        for item in cart_items:
            product = item.product
            quantity = item.quantity

            if quantity > product.available_stock:
                transaction.set_rollback(True)
                return Response({"error": f"Only {product.available_stock} items available for {product.title}."}, status=400)

            # Use discounted_price if exists, else product.price
            product_price = Decimal(str(getattr(product, "discounted_price", product.price)))

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product_price
            )

            total_amount += Decimal(str(product.price)) * quantity
            discounted_amount += product_price * quantity

            # Update stock
            product.available_stock -= quantity
            product.save(update_fields=["available_stock"])

        # Base final amount = discounted_amount
        final_amount = discounted_amount

        # Apply coupon if provided
        coupon = None
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True)
                now = timezone.now()
                if coupon.valid_from and coupon.valid_from > now:
                    return Response({"error": "Coupon is not yet valid"}, status=400)
                if coupon.valid_to and coupon.valid_to < now:
                    return Response({"error": "Coupon has expired"}, status=400)

                # Apply coupon to each product price
                temp_final = Decimal("0.00")
                for item in cart_items:
                    product_price = Decimal(str(getattr(item.product, "discounted_price", item.product.price)))

                    if coupon.discount_type == "percentage":
                        product_price -= product_price * Decimal(str(coupon.discount_value)) / Decimal("100")
                    else:  # fixed
                        product_price -= Decimal(str(coupon.discount_value))

                    temp_final += max(product_price * item.quantity, Decimal("0.00"))

                final_amount = max(temp_final, Decimal("0.00"))
                CouponRedemption.objects.get_or_create(coupon=coupon, user=user)

            except Coupon.DoesNotExist:
                return Response({"error": "Invalid coupon code"}, status=400)

        # Prevent checkout if final_amount <= 0
        if final_amount <= 0:
            return Response({"error": "Final order amount is 0 or negative, cannot proceed to checkout"}, status=400)

        # Save order totals
        order.total_amount = total_amount
        order.discounted_amount = discounted_amount
        order.final_amount = final_amount
        order.coupon = coupon
        order.save(update_fields=["total_amount", "discounted_amount", "final_amount", "coupon"])

        # Clear cart
        cart_items.delete()

        return Response({
            "success": "Order placed successfully",
            "order_id": order.id,
            "order_number": order.order_number,
            "total_amount": str(total_amount),
            "discounted_amount": str(discounted_amount),
            "final_amount": str(final_amount),
            "coupon_code": coupon.code if coupon else None
        }, status=201)

# order details views
class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product")




class OrderTrackingView(generics.ListAPIView):
    serializer_class = OrderTrackingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        order_identifier = self.kwargs.get("order_identifier")
        user = self.request.user

        try:
            if order_identifier.isdigit():
                order = Order.objects.get(id=int(order_identifier))
            else:
                order = Order.objects.get(order_number=order_identifier)
        except Order.DoesNotExist:
            return OrderTracking.objects.none()

        if not user.is_staff and order.user != user:
            return OrderTracking.objects.none()

        return order.tracking_history.all().order_by("created_at")




class OrderTrackingDetailView(generics.RetrieveAPIView):
    queryset = OrderTracking.objects.all().select_related('order', 'updated_by', 'order__user', 'order__shipping_address')
    serializer_class = OrderTrackingSerializer
    permission_classes = [permissions.IsAuthenticated]




from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser
from .serializers import OrderListSerializer
from .models import Order

class OrderListFilter(generics.ListAPIView):
    """
    List all orders with searching and filtering.
    Search by customer email or order_number.
    Filter by order_status.
    """
    queryset = Order.objects.select_related('user', 'shipping_address').all().order_by('-created_at')
    serializer_class = OrderListSerializer
    permission_classes = [IsAdminUser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['order_status']  # filter by status
    search_fields = ['user__email', 'user_name', 'order_number']  # search by customer email or order number
    ordering_fields = ['created_at', 'total_amount']  # optional ordering
    ordering = ['-created_at']





from rest_framework import generics, status
from rest_framework.response import Response
from decimal import Decimal
from .serializers import BuyNowSerializer
from b2c.orders.models import Order
from b2c.coupons.models import Coupon, CouponRedemption

from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import BuyNowSerializer

class BuyNowView(generics.CreateAPIView):
    serializer_class = BuyNowSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        if order.payment_method == "ONLINE":
            return Response({
                "order_id": order.id,
                "final_amount": str(order.final_amount),
                "message": "Order created. Please complete payment via Stripe."
            }, status=status.HTTP_201_CREATED)

        return Response({
            "order_id": order.id,
            "final_amount": str(order.final_amount),
            "message": "Order placed successfully (COD)"
        }, status=status.HTTP_201_CREATED)




class AdminOrderListView(generics.ListAPIView):
    """
    Admin view to list all orders with search, filter, and ordering.
    """
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["order_status", "payment_status", "payment_method", "is_paid"]
    search_fields = ["order_number", "user__email", "items__product__title"]
    ordering_fields = ["created_at", "total_amount"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            return Order.objects.none()  # non-admin cannot access
        # Use select_related and prefetch_related for performance
        return Order.objects.select_related("shipping_address", "user") \
                            .prefetch_related("items__product", "tracking_history") \
                            .order_by("-created_at")
