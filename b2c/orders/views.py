from rest_framework import generics, status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer
from b2c.cart.models import CartItem
from b2c.checkout.models import Shipping

from rest_framework.permissions import IsAuthenticated  # or AllowAny
from rest_framework.response import Response
from rest_framework import generics

class OrderSummaryView(generics.RetrieveAPIView):
    # parser_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]  # or [AllowAny]

    def get(self, request, *args, **kwargs):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)
        shipping = Shipping.objects.filter(user=user).last()

        summary = {
            "shipping_address": str(shipping) if shipping else None,
            "cart_items": [
                {
                    "product": item.product.name,
                    "quantity": item.quantity,
                    "price": item.product.price
                }
                for item in cart_items
            ]
        }
        return Response(summary)
    parser_classes = [AllowAny]

    



class PlaceOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can place order

    def create(self, request, *args, **kwargs):
        user = request.user

        cart_items = CartItem.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        shipping = Shipping.objects.filter(user=user).last()
        if not shipping:
            return Response({"detail": "Shipping info missing"}, status=status.HTTP_400_BAD_REQUEST)

        # Create order
        order = Order.objects.create(
            user=user,
            shipping_address=str(shipping)
        )

        # Add items to order
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_item=item.product.price
            )

        cart_items.delete()  # Clear the cart after placing the order

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class CreateOrderView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated]
   
