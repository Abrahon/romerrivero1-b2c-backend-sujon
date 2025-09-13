from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import generics, filters, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from b2c.cart.models import CartItem
from b2c.checkout.models import Shipping
from b2c.products.models import Products
from b2c.orders.models import Order, OrderItem, OrderTracking
from b2c.orders.serializers import OrderItemSerializer, OrderDetailSerializer, OrderTrackingSerializer
from notifications.models import Notification
from rest_framework.views import APIView



class OrderListView(generics.ListAPIView):
    """
    GET /api/orders/ -> Paginated list of orders for the authenticated user.
    Supports: search (order_number, product name), filter (order_status, payment_status), ordering.
    """
    serializer_class = OrderDetailSerializer  # Use OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["order_status", "payment_status"]
    search_fields = ["order_number", "items__product__name"]
    ordering_fields = ["created_at", "total_amount"]

    def get_queryset(self):
        # Only fetch orders that belong to the authenticated user
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("user")
            .prefetch_related("items__product")  # prefetch related items and products
            .order_by("-created_at")
        )



class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user

        # Get shipping object for the user
        shipping_id = request.data.get("shipping_id")
        if not shipping_id:
            return Response(
                {"error": "shipping_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        shipping = get_object_or_404(Shipping, id=shipping_id, user=user)

        # Create order with Shipping object (not string)
        order = Order.objects.create(
            user=user,
            shipping_address=shipping,   # ✅ pass the object
            total_amount=Decimal("0.00"),
            payment_status="pending",
            order_status="PENDING",
        )

        # Add cart items into order items
        cart_items = CartItem.objects.filter(user=user)
        if not cart_items.exists():
            return Response(
                {"error": "No items in cart"},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_amount = Decimal("0.00")
        for item in cart_items:
            product = item.product
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price
            )
            total_amount += product.price * item.quantity

        # Update total amount
        order.total_amount = total_amount
        order.save()

        # Clear cart after placing order
        cart_items.delete()

        return Response(
            {"message": "Order placed successfully", "order_id": order.id},
            status=status.HTTP_201_CREATED
        )


class OrderDetailView(generics.RetrieveAPIView):
    """
    GET /api/orders/<pk>/ -> Detailed order (items + metadata).
    """
    permission_classes = [IsAuthenticated]  
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        # Ensure the user can only view their own orders
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product")



class OrderTrackingView(generics.ListAPIView):
    serializer_class = OrderTrackingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        order_identifier = self.kwargs.get("order_identifier")
        user = self.request.user

        # Lookup by numeric ID or order number
        if order_identifier.isdigit():
            order = Order.objects.filter(id=int(order_identifier)).first()
        else:
            order = Order.objects.filter(order_number=order_identifier).first()

        # Check if order exists and belongs to user (unless admin)
        if not order or (not user.is_staff and order.user != user):
            return OrderTracking.objects.none()  # returns empty queryset

        # Return tracking history (can be empty)
        return order.tracking_history.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset is None:  # just in case
            return Response(
                {"detail": "Order not found or access denied."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
