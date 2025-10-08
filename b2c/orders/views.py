from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, filters, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
# b2c/orders/views.py
from rest_framework import generics, permissions, status
from .models import Order
from .serializers import AdminOrderStatusUpdateSerializer
from notifications.models import Notification  
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAdminUser
from .serializers import OrderListSerializer
# Models
from b2c.cart.models import CartItem
from b2c.checkout.models import Shipping
from b2c.products.models import Products
from b2c.orders.models import Order, OrderItem, OrderTracking
from b2c.coupons.models import Coupon, CouponRedemption
from notifications.models import Notification
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from datetime import timedelta
from rest_framework import generics, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser
from .models import Order
from .serializers import OrderListSerializer
# Serializers
from b2c.orders.serializers import (
    OrderItemSerializer,
    OrderDetailSerializer,
    OrderTrackingSerializer,
    BuyNowSerializer,
)

User = get_user_model()


class OrderListView(generics.ListAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAdminUser] 
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["order_status", "payment_status"]
    search_fields = ["order_number", "items__product__title"]
    ordering_fields = ["created_at", "total_amount"]

    def get_queryset(self):
        return Order.objects.all().select_related("shipping_address").prefetch_related("items__product").order_by("-created_at")




class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        shipping_id = request.data.get("shipping_id")
        cart_item_ids = request.data.get("cart_item_ids", [])
        coupon_code = request.data.get("coupon_code")
        payment_method = request.data.get("payment_method", "COD")

        if not shipping_id or not cart_item_ids:
            return Response({"error": "shipping_id and cart_item_ids are required"}, status=400)

        shipping = get_object_or_404(Shipping, id=shipping_id, user=user)
        cart_items = CartItem.objects.filter(user=user, id__in=cart_item_ids).select_related("product")
        if not cart_items.exists():
            return Response({"error": "Selected cart items not found"}, status=400)

        # Step 1: Create order (empty amounts first)
        order = Order.objects.create(
            user=user,
            shipping_address=shipping,
            total_amount=Decimal("0.00"),
            discounted_amount=Decimal("0.00"),
            final_amount=Decimal("0.00"),
            payment_status="pending",
            order_status="PENDING",
            payment_method=payment_method
        )

        total_amount = Decimal("0.00")
        discounted_amount = Decimal("0.00")
        final_amount = Decimal("0.00")

        # Step 2: Calculate totals & create items
        for item in cart_items:
            product = item.product
            quantity = item.quantity

            if quantity > product.available_stock:
                transaction.set_rollback(True)
                return Response({"error": f"Only {product.available_stock} items available for {product.title}."}, status=400)

            # Use discounted price if exists
            product_price = Decimal(str(getattr(product, "discounted_price", product.price)))

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product_price
            )

            total_amount += Decimal(str(product.price)) * quantity
            discounted_amount += product_price * quantity

            # Reduce stock
            product.available_stock -= quantity
            product.save(update_fields=["available_stock"])

        # Base final amount = discounted_amount
        final_amount = discounted_amount

        # Step 3: Apply coupon if any
        coupon = None
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True)
                now = timezone.now()
                if coupon.valid_from and coupon.valid_from > now:
                    return Response({"error": "Coupon is not yet valid"}, status=400)
                if coupon.valid_to and coupon.valid_to < now:
                    return Response({"error": "Coupon has expired"}, status=400)

                # Apply coupon
                temp_final = Decimal("0.00")
                for item in cart_items:
                    product_price = Decimal(str(getattr(item.product, "discounted_price", item.product.price)))
                    if coupon.discount_type == "percentage":
                        product_price -= product_price * Decimal(str(coupon.discount_value)) / Decimal("100")
                    else:
                        product_price -= Decimal(str(coupon.discount_value))
                    temp_final += max(product_price * item.quantity, Decimal("0.00"))

                final_amount = max(temp_final, Decimal("0.00"))
                CouponRedemption.objects.get_or_create(coupon=coupon, user=user)

            except Coupon.DoesNotExist:
                return Response({"error": "Invalid coupon code"}, status=400)

        if final_amount <= 0:
            return Response({"error": "Final order amount is 0 or negative, cannot proceed to checkout"}, status=400)

        # Step 4: Save totals
        order.total_amount = total_amount
        order.discounted_amount = discounted_amount
        order.final_amount = final_amount
        order.coupon = coupon

        # COD orders get delivery date immediately
        if payment_method == "COD":
            order.estimated_delivery = timezone.now() + timedelta(days=5)

        order.save(update_fields=["total_amount", "discounted_amount", "final_amount", "coupon", "estimated_delivery"])

        # Step 5: Clear cart
        cart_items.delete()

        # Step 6: Create tracking entry
        OrderTracking.objects.create(
            order=order,
            status="PENDING",
            note="Order placed by customer"
        )

        # Step 7: Send confirmation email (correct totals now)
        send_mail(
            subject=f"Order Confirmation - {order.order_number}",
            message=(
                f"Hello {user.email},\n\n"
                f"Your order {order.order_number} has been confirmed.\n"
                f"Total Amount: {order.final_amount}\n\n"
                "Thank you for shopping with us!"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({
            "success": "Order placed successfully",
            "order_id": order.id,
            "order_number": order.order_number,
            "total_amount": str(total_amount),
            "discounted_amount": str(discounted_amount),
            "final_amount": str(final_amount),
            "coupon_code": coupon.code if coupon else None,
            "estimated_delivery": order.estimated_delivery
        }, status=201)


# order details views
# class OrderDetailView(generics.RetrieveAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = OrderDetailSerializer

#     def get_queryset(self):
#         return Order.objects.filter(user=self.request.user).prefetch_related("items__product")

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderDetailSerializer

class UserOrderHistoryView(generics.ListAPIView):
    """
    List all orders for the authenticated user (complete order history)
    """
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter all orders for the logged-in user
        return Order.objects.filter(user=self.request.user)\
                            .select_related("shipping_address")\
                            .prefetch_related("items__product")\
                            .order_by("-created_at")  # latest orders first

# order tracking by order id 
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


# order tracking by order number 
class OrderTrackingView(generics.RetrieveAPIView):
    serializer_class = OrderTrackingSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only the user can access their orders

    def get_object(self):
        order_identifier = self.kwargs.get("order_identifier")  # e.g., "ORD-20250929223618-1e874b"
        
        # Get the order based on order_number
        order = get_object_or_404(Order, order_number=order_identifier, user=self.request.user)

        # Get all tracking records for this order (optional: latest first)
        tracking_qs = OrderTracking.objects.filter(order=order).select_related(
            "updated_by", "order", "order__user", "order__shipping_address"
        ).order_by("-created_at")

        if not tracking_qs.exists():
            # Optionally, create initial tracking if missing
            tracking = OrderTracking.objects.create(
                order=order,
                status="PENDING",
                note="Order automatically created"
            )
            tracking_qs = OrderTracking.objects.filter(order=order).order_by("-created_at")

        return tracking_qs.first()  # Retrieve latest tracking entry



# order list filter 


class OrderListFilter(generics.ListAPIView):
    """
    List all orders with searching and filtering.
    Search by order number, customer email, or name.
    Filter by order_status.
    """
    queryset = Order.objects.select_related('user', 'shipping_address').all().order_by('-created_at')
    serializer_class = OrderListSerializer
    permission_classes = [IsAdminUser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['order_status']

    search_fields = [
        'order_number',
        'user__email',
        'user__name',
        'shipping_address__full_name',
        'shipping_address__email'
    ]

    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if not queryset.exists():
            return Response(
                {"message": "No orders found for the given search or filters."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)








# admin update status 
class AdminUpdateOrderStatusView(generics.UpdateAPIView):
    serializer_class = AdminOrderStatusUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Order.objects.all()
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Optional: Send notification to user
        Notification.objects.create(
            user=order.user,
            title=f"Order {order.order_number} status updated",
            message=f"Your order status has been updated to '{order.order_status}'."
        )

        return Response({
            "message": f"Order {order.order_number} status updated successfully.",
            "order_id": order.id,
            "new_status": order.order_status
        }, status=status.HTTP_200_OK)



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
    permission_classes = [IsAdminUser]
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

# delete order 

class OrderDeleteView(generics.DestroyAPIView):
    """
    Delete an order by ID (Admin only).
    """
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        try:
            order = self.get_queryset().get(pk=order_id)
            order.delete()
            return Response(
                {"message": f"Order #{order_id} deleted successfully."},
                status=status.HTTP_204_NO_CONTENT
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )
