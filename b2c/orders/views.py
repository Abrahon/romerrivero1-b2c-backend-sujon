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

from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order
from .serializers import OrderListSerializer
from .serializers import OrderTrackingSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


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
    Place an order from the user's cart + latest shipping
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user

        cart_qs = CartItem.objects.filter(user=user).select_related("product")
        if not cart_qs.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        shipping = Shipping.objects.filter(user=user).last()
        if not shipping:
            return Response({"detail": "Shipping information missing."}, status=status.HTTP_400_BAD_REQUEST)

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

            if product.stock < qty:
                transaction.set_rollback(True)
                return Response(
                    {"detail": f"Insufficient stock for {product.name}."}, status=status.HTTP_400_BAD_REQUEST
                )
            product.stock -= qty
            product.save(update_fields=["stock"])

            OrderItem.objects.create(order=order, product=product, quantity=qty, price_at_time=price)
            total += price * qty

        order.total_amount = total
        order.save(update_fields=["total_amount"])

        cart_qs.delete()

        # Send notification to the user
        notification = Notification.objects.create(
            user=user,
            title="Order Placed",
            message=f"Your order #{order.id} has been placed successfully. Total: {total}"
        )

        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)




class OrderDetailView(generics.RetrieveAPIView):
    """
    GET /api/orders/<pk>/ -> Detailed order (items + metadata).
    """
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this view
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        # Ensure the user can only view their own orders
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product")




# class OrderTrackingView(generics.RetrieveAPIView):
#     """
#     Track order by order_number or id.
#     Example: /api/orders/track/<order_id_or_number>/
#     """
#     serializer_class = OrderTrackingSerializer
#     permission_classes = [IsAuthenticated]
#     # permission_classes = [AllowAny]
    
    
#     def get_queryset(self):
           
#            order_identifier = self.kwargs.get("pk")
#            try:
#             # First try by ID
#             return Order.objects.get(id=order_identifier, user=self.request.user)
#            except Order.DoesNotExist:
               
#             try:
#                 return Order.objects.get(order_number=order_identifier, user=self.request.user)
#             except Order.DoesNotExist:
#                 return None
            
#     def get(self, request, *args, **kwargs):
#         order = self.get_object()
#         if not order:
#             return Response(
#                 {"detail": "Order not found or you don’t have permission."},
#                 status=status.HTTP_404_NOT_FOUND,
#             )
#         serializer = self.get_serializer(order)
#         return Response(serializer.data, status=status.HTTP_200_OK)

            
#         # Ensure the user can only view their own orders
#         # return Order.objects.filter(user=self.request.user).select_related("user")

class OrderTrackingView(generics.RetrieveAPIView):
    serializer_class = OrderTrackingSerializer
    lookup_url_kwarg = "order_identifier"

    def get_object(self):
        order_identifier = self.kwargs.get("order_identifier")

        if not order_identifier:  # safety check
            return None

        # Case 1: Numeric ID
        if order_identifier.isdigit():
            return Order.objects.filter(id=int(order_identifier)).first()

        # Case 2: Order Number (string with hyphen etc.)
        return Order.objects.filter(order_number=order_identifier).first()

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        if order:
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
