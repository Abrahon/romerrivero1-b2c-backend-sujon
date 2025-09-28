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




# class PlaceOrderView(APIView):
#     permission_classes = [IsAuthenticated]

#     @transaction.atomic
#     def post(self, request):
#         user = request.user
#         shipping_id = request.data.get("shipping_id")
#         cart_item_ids = request.data.get("cart_item_ids", []) 

#         if not shipping_id:
#             return Response({"error": "shipping_id is required"}, status=400)

#         if not cart_item_ids:
#             return Response({"error": "cart_item_ids is required"}, status=400)

#         shipping = get_object_or_404(Shipping, id=shipping_id, user=user)

#         # Fetch only selected cart items
#         cart_items = CartItem.objects.filter(user=user, id__in=cart_item_ids).select_related("product")
#         if not cart_items.exists():
#             return Response({"error": "Selected cart items not found"}, status=400)

#         # Create order
#         order = Order.objects.create(
#             user=user,
#             shipping_address=shipping,
#             total_amount=Decimal("0.00"),
#             payment_status="pending",
#             order_status="PENDING",
#         )

#         total_amount = Decimal("0.00")
#         for item in cart_items:
#             product = item.product
#             if item.quantity > product.available_stock:
#                 transaction.set_rollback(True)
#                 return Response(
#                     {"error": f"Only {product.available_stock} items available for {product.title}."},
#                     status=400,
#                 )

#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 quantity=item.quantity,
#                 price=product.discounted_price if hasattr(product, "discounted_price") else product.price,
#             )

#             total_amount += (
#                 (product.discounted_price if hasattr(product, "discounted_price") else product.price)
#                 * item.quantity
#             )

#             # Reduce stock
#             product.available_stock -= item.quantity
#             product.save(update_fields=["available_stock"])

#         order.total_amount = total_amount
#         order.discounted_amount = total_amount
#         order.save(update_fields=["total_amount", "discounted_amount"])

#         # ✅ Create first tracking entry (important!)
#         from b2c.orders.models import OrderTracking
#         OrderTracking.objects.create(
#             order=order,
#             status=order.order_status,   # "PENDING"
#             updated_by=user,             # user who placed the order
#             note="Order placed successfully"
#         )

#         # Clear only the ordered cart items
#         cart_items.delete()

#         # Customer notification
#         Notification.objects.create(
#             user=user,
#             title="Order Placed",
#             message=f"Your order {order.order_number} has been placed successfully.",
#         )

#         # Admin notifications
#         admins = User.objects.filter(is_staff=True)
#         for admin in admins:
#             Notification.objects.create(
#                 user=admin,
#                 title="New Order",
#                 message=f"New order {order.order_number} placed by {user.email}.",
#             )

#         return Response(
#             {
#                 "success": "Order placed successfully",
#                 "order_id": order.id,
#                 "order_number": order.order_number   # ✅ include for tracking
#             },
#             status=201
#         )

from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from b2c.orders.models import Order, OrderItem, OrderTracking
from b2c.cart.models import CartItem

from b2c.coupons.models import Coupon

# class PlaceOrderView(APIView):
#     permission_classes = [IsAuthenticated]

#     @transaction.atomic
#     def post(self, request):
#         user = request.user
#         shipping_id = request.data.get("shipping_id")
#         cart_item_ids = request.data.get("cart_item_ids", [])
#         coupon_code = request.data.get("coupon_code")  # optional

#         if not shipping_id or not cart_item_ids:
#             return Response({"error": "shipping_id and cart_item_ids are required"}, status=400)

#         shipping = get_object_or_404(Shipping, id=shipping_id, user=user)
#         cart_items = CartItem.objects.filter(user=user, id__in=cart_item_ids).select_related("product")
#         if not cart_items.exists():
#             return Response({"error": "Selected cart items not found"}, status=400)

#         # Create order with 0 amounts first
#         order = Order.objects.create(
#             user=user,
#             shipping_address=shipping,
#             total_amount=Decimal("0.00"),
#             discounted_amount=Decimal("0.00"),
#             final_amount=Decimal("0.00"),
#             payment_status="pending",
#             order_status="PENDING",
#         )

#         total_amount = Decimal("0.00")        # Original prices
#         discounted_amount = Decimal("0.00")   # Sum of discounted product prices

#         for item in cart_items:
#             product = item.product
#             if item.quantity > product.available_stock:
#                 transaction.set_rollback(True)
#                 return Response(
#                     {"error": f"Only {product.available_stock} items available for {product.title}."},
#                     status=400,
#                 )

#             # Use discounted price if exists, otherwise original price
#             price_to_use = product.discounted_price if getattr(product, "discounted_price", None) else product.price

#             # Create order item
#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 quantity=item.quantity,
#                 price=price_to_use,
#             )

#             # Sum totals
#             total_amount += product.price * item.quantity
#             discounted_amount += price_to_use * item.quantity

#             # Reduce stock
#             product.available_stock -= item.quantity
#             product.save(update_fields=["available_stock"])

#         # Apply coupon if exists
#         final_amount = discounted_amount
#         if coupon_code:
#             try:
#                 coupon = Coupon.objects.get(code=coupon_code, active=True)
#                 if coupon.discount_type == "percentage":
#                     discount_amount = (final_amount * Decimal(coupon.discount_value)) / Decimal("100")
#                 else:  # fixed discount
#                     discount_amount = Decimal(coupon.discount_value)
#                 final_amount -= discount_amount
#                 final_amount = max(final_amount, Decimal("0.00"))

#                 # Record redemption
#                 from b2c.coupons.models import CouponRedemption
#                 CouponRedemption.objects.get_or_create(coupon=coupon, user=user)

#                 order.coupon_code = coupon_code
#             except Coupon.DoesNotExist:
#                 pass

#         # Save order amounts
#         order.total_amount = total_amount
#         order.discounted_amount = discounted_amount
#         order.final_amount = final_amount
#         order.save(update_fields=["total_amount", "discounted_amount", "final_amount"])


#         # Create first tracking entry
#         OrderTracking.objects.create(
#             order=order,
#             status=order.order_status,
#             updated_by=user,
#             note="Order placed successfully"
#         )

#         # Clear cart items
#         cart_items.delete()

#         # Notifications
#         Notification.objects.create(
#             user=user,
#             title="Order Placed",
#             message=f"Your order {order.order_number} has been placed successfully.",
#         )
#         for admin in User.objects.filter(is_staff=True):
#             Notification.objects.create(
#                 user=admin,
#                 title="New Order",
#                 message=f"New order {order.order_number} placed by {user.email}.",
#             )

#         return Response({
#             "success": "Order placed successfully",
#             "order_id": order.id,
#             "order_number": order.order_number,
#             "final_amount": str(order.final_amount),
#         }, status=201)

from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from b2c.orders.models import Order, OrderItem, OrderTracking
from b2c.cart.models import CartItem
from b2c.coupons.models import Coupon, CouponRedemption
from b2c.checkout.models import Shipping
from accounts.models import User


# class PlaceOrderView(APIView):
#     permission_classes = [IsAuthenticated]

#     @transaction.atomic
#     def post(self, request):
#         user = request.user
#         shipping_id = request.data.get("shipping_id")
#         cart_item_ids = request.data.get("cart_item_ids", [])

#         if not shipping_id or not cart_item_ids:
#             return Response({"error": "shipping_id and cart_item_ids are required"}, status=400)

#         shipping = get_object_or_404(Shipping, id=shipping_id, user=user)
#         cart_items = CartItem.objects.filter(user=user, id__in=cart_item_ids).select_related("product")
#         if not cart_items.exists():
#             return Response({"error": "Selected cart items not found"}, status=400)

#         # Create order with temporary amounts
#         order = Order.objects.create(
#             user=user,
#             shipping_address=shipping,
#             total_amount=Decimal("0.00"),
#             discounted_amount=Decimal("0.00"),
#             final_amount=Decimal("0.00"),
#             payment_status="pending",
#             order_status="PENDING",
#         )

#         total_amount = Decimal("0.00")
#         discounted_amount = Decimal("0.00")

#         # Process cart items
#         for item in cart_items:
#             product = item.product
#             if item.quantity > product.available_stock:
#                 transaction.set_rollback(True)
#                 return Response(
#                     {"error": f"Only {product.available_stock} items available for {product.title}."},
#                     status=400,
#                 )

#             # Prefer product's discounted price if set
#             price_to_use = getattr(product, "discounted_price", None) or product.price

#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 quantity=item.quantity,
#                 price=price_to_use,
#             )

#             total_amount += product.price * item.quantity
#             discounted_amount += price_to_use * item.quantity

#             # Reduce stock
#             product.available_stock -= item.quantity
#             product.save(update_fields=["available_stock"])

#         # Base final amount = product-discounted sum
#         final_amount = discounted_amount

#         # ✅ Apply coupon only if provided
#         if "coupon_code" in request.data and request.data["coupon_code"]:
#             try:
#                 coupon = Coupon.objects.get(code=request.data["coupon_code"], active=True)

#                 if coupon.discount_type == "percentage":
#                     discount_amount = (final_amount * Decimal(coupon.discount_value)) / Decimal("100")
#                 else:
#                     discount_amount = Decimal(coupon.discount_value)

#                 final_amount -= discount_amount
#                 final_amount = max(final_amount, Decimal("0.00"))

#                 CouponRedemption.objects.get_or_create(coupon=coupon, user=user)

#                 if hasattr(order, "coupon"):
#                     order.coupon = coupon

#             except Coupon.DoesNotExist:
#                 pass

#         # Save updated amounts
#         order.total_amount = total_amount
#         order.discounted_amount = discounted_amount
#         order.final_amount = final_amount
#         if hasattr(order, "coupon"):
#             order.save(update_fields=["total_amount", "discounted_amount", "final_amount", "coupon"])
#         else:
#             order.save(update_fields=["total_amount", "discounted_amount", "final_amount"])

#         # Create first tracking
#         OrderTracking.objects.create(
#             order=order,
#             status=order.order_status,
#             updated_by=user,
#             note="Order placed successfully"
#         )

#         # Clear cart
#         cart_items.delete()

#         # Notifications
#         Notification.objects.create(
#             user=user,
#             title="Order Placed",
#             message=f"Your order {order.order_number} has been placed successfully.",
#         )
#         for admin in User.objects.filter(is_staff=True):
#             Notification.objects.create(
#                 user=admin,
#                 title="New Order",
#                 message=f"New order {order.order_number} placed by {user.email}.",
#             )

#         return Response({
#             "success": "Order placed successfully",
#             "order_id": order.id,
#             "order_number": order.order_number,
#             "final_amount": str(order.final_amount),
#         }, status=201)

# from decimal import Decimal
# from django.db import transaction
# from django.shortcuts import get_object_or_404
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response

# from b2c.orders.models import Order, OrderItem, OrderTracking
# from b2c.cart.models import CartItem
# from b2c.coupons.models import Coupon, CouponRedemption

# class PlaceOrderView(APIView):
#     permission_classes = [IsAuthenticated]

#     @transaction.atomic
#     def post(self, request):
#         user = request.user
#         shipping_id = request.data.get("shipping_id")
#         cart_item_ids = request.data.get("cart_item_ids", [])

#         if not shipping_id or not cart_item_ids:
#             return Response({"error": "shipping_id and cart_item_ids are required"}, status=400)

#         shipping = get_object_or_404(Shipping, id=shipping_id, user=user)
#         cart_items = CartItem.objects.filter(user=user, id__in=cart_item_ids).select_related("product")
#         if not cart_items.exists():
#             return Response({"error": "Selected cart items not found"}, status=400)

#         # Create order with temporary amounts
#         order = Order.objects.create(
#             user=user,
#             shipping_address=shipping,
#             total_amount=Decimal("0.00"),
#             discounted_amount=Decimal("0.00"),
#             final_amount=Decimal("0.00"),
#             payment_status="pending",
#             order_status="PENDING",
#         )

#         total_amount = Decimal("0.00")
#         discounted_amount = Decimal("0.00")

#         def get_final_price(product, order_coupon=None):
#             """Calculate final price after product discount + coupon discount."""
#             product_price = getattr(product, "price", 0) or 0
#             # Product discount first
#             product_discount = getattr(product, "discount", 0) or 0
#             if product_discount > 0:
#                 product_price -= product_price * product_discount / 100

#             # Coupon discount next
#             if order_coupon:
#                 coupon_discount = getattr(order_coupon, "discount_percentage", 0) or 0
#                 if coupon_discount > 0:
#                     product_price -= product_price * coupon_discount / 100

#             return max(round(product_price, 2), 0)

#         # Process cart items
#         for item in cart_items:
#             product = item.product
#             if item.quantity > product.available_stock:
#                 transaction.set_rollback(True)
#                 return Response(
#                     {"error": f"Only {product.available_stock} items available for {product.title}."},
#                     status=400,
#                 )

#             # Base price for order item (before coupon)
#             price_to_use = getattr(product, "discounted_price", None) or product.price

#             # Create order item
#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 quantity=item.quantity,
#                 price=price_to_use,
#             )

#             total_amount += product.price * item.quantity
#             discounted_amount += price_to_use * item.quantity

#             # Reduce stock
#             product.available_stock -= item.quantity
#             product.save(update_fields=["available_stock"])

#         # Apply coupon if provided
#         order_coupon = None
#         final_amount = discounted_amount
#         if "coupon_code" in request.data and request.data["coupon_code"]:
#             try:
#                 order_coupon = Coupon.objects.get(code=request.data["coupon_code"], active=True)
#                 for item in cart_items:
#                     product = item.product
#                     final_amount_item = get_final_price(product, order_coupon)
#                     final_amount += (final_amount_item - price_to_use) * item.quantity  # adjust final amount
#                 final_amount = max(final_amount, Decimal("0.00"))

#                 CouponRedemption.objects.get_or_create(coupon=order_coupon, user=user)
#                 order.coupon = order_coupon
#             except Coupon.DoesNotExist:
#                 pass

#         # Save updated amounts
#         order.total_amount = total_amount
#         order.discounted_amount = discounted_amount
#         order.final_amount = final_amount
#         order.save(update_fields=["total_amount", "discounted_amount", "final_amount", "coupon"] if order_coupon else ["total_amount", "discounted_amount", "final_amount"])

#         # Create first tracking
#         OrderTracking.objects.create(
#             order=order,
#             status=order.order_status,
#             updated_by=user,
#             note="Order placed successfully"
#         )

#         # Clear cart
#         cart_items.delete()

#         # Notifications
#         Notification.objects.create(
#             user=user,
#             title="Order Placed",
#             message=f"Your order {order.order_number} has been placed successfully.",
#         )
#         for admin in User.objects.filter(is_staff=True):
#             Notification.objects.create(
#                 user=admin,
#                 title="New Order",
#                 message=f"New order {order.order_number} placed by {user.email}.",
#             )

#         return Response({
#             "success": "Order placed successfully",
#             "order_id": order.id,
#             "order_number": order.order_number,
#             "final_amount": str(order.final_amount),
#         }, status=201)
from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from b2c.orders.models import Order, OrderItem, OrderTracking
from b2c.cart.models import CartItem
from b2c.coupons.models import Coupon, CouponRedemption

class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        shipping_id = request.data.get("shipping_id")
        cart_item_ids = request.data.get("cart_item_ids", [])

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

        # Function to calculate final price per product
        def get_final_price(product, order_coupon=None):
            product_price = getattr(product, "price", 0) or 0
            product_discount = getattr(product, "discount", 0) or 0
            if product_discount > 0:
                product_price -= product_price * product_discount / 100
            if order_coupon:
                coupon_discount = getattr(order_coupon, "discount_percentage", 0) or 0
                if coupon_discount > 0:
                    product_price -= product_price * coupon_discount / 100
            return max(round(product_price, 2), 0)

        # Create order items
        for item in cart_items:
            product = item.product
            if item.quantity > product.available_stock:
                transaction.set_rollback(True)
                return Response({"error": f"Only {product.available_stock} items available for {product.title}."}, status=400)

            price_to_use = getattr(product, "discounted_price", None) or product.price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=price_to_use,
            )

            total_amount += product.price * item.quantity
            discounted_amount += price_to_use * item.quantity

            product.available_stock -= item.quantity
            product.save(update_fields=["available_stock"])

        final_amount = discounted_amount
        order_coupon = None

        # Apply coupon if provided
        if request.data.get("coupon_code"):
            try:
                order_coupon = Coupon.objects.get(code=request.data["coupon_code"], active=True)
                # recalculate final amount using product + coupon discount
                final_amount = sum(get_final_price(item.product, order_coupon) * item.quantity for item in cart_items)
                final_amount = max(final_amount, Decimal("0.00"))

                CouponRedemption.objects.get_or_create(coupon=order_coupon, user=user)
                order.coupon = order_coupon
            except Coupon.DoesNotExist:
                pass

        order.total_amount = total_amount
        order.discounted_amount = discounted_amount
        order.final_amount = final_amount
        order.save(update_fields=["total_amount", "discounted_amount", "final_amount", "coupon"] if order_coupon else ["total_amount", "discounted_amount", "final_amount"])

        # Create first tracking
        OrderTracking.objects.create(order=order, status=order.order_status, updated_by=user, note="Order placed successfully")

        # Clear cart
        cart_items.delete()

        return Response({
            "success": "Order placed successfully",
            "order_id": order.id,
            "order_number": order.order_number,
            "final_amount": str(order.final_amount),
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
    queryset = OrderTracking.objects.all().select_related('order', 'updated_by')
    serializer_class = OrderTrackingSerializer
    permission_classes = [permissions.IsAuthenticated]



class BuyNowView(generics.CreateAPIView):
    serializer_class = BuyNowSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        if order.payment_method == "ONLINE":
            # Stripe payment is handled by your payment app
            return Response({
                "order_id": order.id,
                "message": "Order created. Please complete payment via Stripe."
            }, status=status.HTTP_201_CREATED)

        # COD order
        return Response({
            "order_id": order.id,
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
