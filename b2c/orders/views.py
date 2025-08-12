from decimal import Decimal
from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from b2c.cart.models import CartItem
from b2c.checkout.models import Shipping
from b2c.products.models import Products
from b2c.orders.models import Order, OrderItem
from b2c.orders.serializers import OrderDetailSerializer
from notifications.models import Notification
# from notifications.utils import send_user_notification
# b2c/orders/views.py
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order
from .serializers import OrderListSerializer

class OrderListView(generics.ListAPIView):
    """
    GET /api/orders/ -> Paginated list of orders for the authenticated user.
    Supports: search (order_number, product name), filter (order_status, payment_status), ordering.
    """
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this
    serializer_class = OrderListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["order_status", "payment_status"]
    search_fields = ["order_number", "items__product__name"]
    ordering_fields = ["created_at", "total_amount"]

    def get_queryset(self):
        # Only fetch orders that belong to the authenticated user
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("user")
            .prefetch_related("items__product")
            .order_by("-created_at")
        )


class PlaceOrderView(generics.CreateAPIView):
    """
    POST /api/orders/place/
    Body: none (uses authenticated user's cart + latest shipping)
    """
    permission_classes = [AllowAny]
    serializer_class = OrderDetailSerializer  # response serializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        
        # Check if the cart is empty
        cart_qs = CartItem.objects.filter(user=user).select_related("product")
        if not cart_qs.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the latest shipping information
        shipping = Shipping.objects.filter(user=user).last()
        if not shipping:
            return Response({"detail": "Shipping information missing."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the order and items within a transaction
        order = Order.objects.create(
            user=user,
            shipping_address=str(shipping),
            total_amount=Decimal("0.00"),
            payment_status="pending",  # Default payment status
            order_status="PENDING"  # Default order status
        )

        total = Decimal("0.00")
        for cart_item in cart_qs:
            product = cart_item.product
            qty = cart_item.quantity
            price = getattr(product, "price", Decimal("0.00"))

            # Stock management (ensure there’s enough stock)
            if hasattr(product, "stock"):
                if product.stock < qty:
                    transaction.set_rollback(True)
                    return Response(
                        {"detail": f"Insufficient stock for {product.name}"}, status=status.HTTP_400_BAD_REQUEST
                    )
                product.stock -= qty
                product.save(update_fields=["stock"])
            elif hasattr(product, "count_in_stock"):
                if product.count_in_stock < qty:
                    transaction.set_rollback(True)
                    return Response(
                        {"detail": f"Insufficient stock for {product.name}"}, status=status.HTTP_400_BAD_REQUEST
                    )
                product.count_in_stock -= qty
                product.save(update_fields=["count_in_stock"])

            # Create the order item
            OrderItem.objects.create(order=order, product=product, quantity=qty, price_at_time=price)
            total += price * qty

        order.total_amount = total
        order.save(update_fields=["total_amount"])

        # Clear the user's cart after the order is placed
        cart_qs.delete()

        # Create a notification for the user
        notification = Notification.objects.create(
            user=user,
            title="Order Placed",
            message=f"Your order #{order.id} has been placed successfully. Total: {total}"
        )
class OrderDetailView(generics.RetrieveAPIView):
    """
    GET /api/orders/<pk>/ -> Detailed order (items + metadata).
    """
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this view
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        # Ensure the user can only view their own orders
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product")
        
        # # Send the user notification
        # send_user_notification(user.id, notification.id)

        # # Optionally, trigger payment processing if needed
        # # process_payment(order)  # Placeholder for actual payment logic

        # # Return the created order data
        # serializer = self.get_serializer(order)
        # return Response(serializer.data, status=status.HTTP_201_CREATED)
