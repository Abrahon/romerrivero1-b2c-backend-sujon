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
    BuyNowSerializer,  # Added BuyNowSerializer
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



class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        shipping_id = request.data.get("shipping_id")

        if not shipping_id:
            return Response({"error": "shipping_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        shipping = get_object_or_404(Shipping, id=shipping_id, user=user)

        cart_items = CartItem.objects.filter(user=user).select_related("product")
        if not cart_items.exists():
            return Response({"error": "No items in cart"}, status=status.HTTP_400_BAD_REQUEST)

        # Create order
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
            if item.quantity > product.available_stock:
                transaction.set_rollback(True)
                return Response(
                    {"error": f"Only {product.available_stock} items available for {product.title}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.discounted_price if hasattr(product, "discounted_price") else product.price,
            )

            total_amount += (
                (product.discounted_price if hasattr(product, "discounted_price") else product.price)
                * item.quantity
            )

            product.available_stock -= item.quantity
            product.save(update_fields=["available_stock"])

        order.total_amount = total_amount
        order.discounted_amount = total_amount
        order.save(update_fields=["total_amount", "discounted_amount"])

        # Clear cart
        cart_items.delete()

        # Customer notification
        Notification.objects.create(
            user=user,
            title="Order Placed",
            message=f"Your order {order.order_number} has been placed successfully.",
        )

        # Admin notifications
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                title="New Order",
                message=f"New order {order.order_number} placed by {user.email}.",
            )

        return Response({"success": "Order placed successfully", "order_id": order.id}, status=status.HTTP_201_CREATED)



class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product")


class OrderTrackingView(generics.ListAPIView):
    serializer_class = OrderTrackingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        order_identifier = self.kwargs.get("order_identifier")
        user = self.request.user

        order = None
        if order_identifier.isdigit():
            order = Order.objects.filter(id=int(order_identifier)).first()
        else:
            order = Order.objects.filter(order_number=order_identifier).first()

        if not order or (not user.is_staff and order.user != user):
            return OrderTracking.objects.none()

        return order.tracking_history.all()


class BuyNowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
      
        data = request.data
        serializer = BuyNowSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response({
            "message": "Order placed successfully",
            "order_id": order.id,
            "order_number": order.order_number
        }, status=status.HTTP_201_CREATED)
