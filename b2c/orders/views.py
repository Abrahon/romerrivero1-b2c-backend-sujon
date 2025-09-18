from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend

from b2c.cart.models import CartItem
from b2c.checkout.models import Shipping
from b2c.products.models import Products
from b2c.orders.models import Order, OrderItem, OrderTracking
from b2c.orders.serializers import OrderItemSerializer, OrderDetailSerializer, OrderTrackingSerializer
from notifications.models import Notification
from .serializers import BuyNowSerializer
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()





class OrderListView(generics.ListAPIView):
    """
    GET /api/orders/ -> Paginated list of orders for the authenticated user.
    Supports: search (order_number, product title), filter (order_status, payment_status), ordering.
    """
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["order_status", "payment_status"]
    search_fields = ["order_number", "items__product__title"]  # FIXED: use 'title' instead of 'name'
    ordering_fields = ["created_at", "total_amount"]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("user")
            .prefetch_related("items__product")
            .order_by("-created_at")
        )


class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        shipping_id = request.data.get("shipping_id")

        if not shipping_id:
            return Response({"error": "shipping_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            shipping = Shipping.objects.get(id=shipping_id, user=user)
        except Shipping.DoesNotExist:
            return Response(
                {"error": f"No Shipping found with id {shipping_id} for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_items = CartItem.objects.filter(user=user).select_related('product')
        if not cart_items.exists():
            return Response({"error": "No items in cart"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=user,
            shipping_address=shipping,
            total_amount=Decimal("0.00"),
            payment_status="pending",
            order_status="PENDING",
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

            # Reduce stock
            product.available_stock -= item.quantity
            product.save(update_fields=['available_stock'])

        order.total_amount = total_amount
        order.save(update_fields=['total_amount'])

        # Clear cart
        cart_items.delete()

        # Notifications
        Notification.objects.create(
            user=user,
            type="ORDER",
            message=f"Your order {order.order_number} has been placed successfully."
        )
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                type="ORDER",
                message=f"New order {order.order_number} placed by {user.email}."
            )

        return Response({"message": "Order placed successfully", "order_id": order.id}, status=status.HTTP_201_CREATED)



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
    permission_classes = [IsAuthenticated]

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


# COD
class BuyNowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BuyNowSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            order = serializer.save()
            # Optional: Create notifications for user and admins here
            return Response({
                "message": "Order placed successfully",
                "order_id": order.id,
                "order_number": order.order_number
            }, status=status.HTTP_201_CREATED)
