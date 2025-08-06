from rest_framework import generics, status
from rest_framework.permissions import AllowAny 
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer
from b2c.cart.models import CartItem
from b2c.checkout.models import Shipping

class OrderSummaryView(generics.RetrieveAPIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    def get(self,request,*args, **kwargs):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)
        shipping = Shipping.objects.filter(user=user).last()

        summary = {
            "shipping_address": str(shipping),
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
    

class PlaceOrderView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = OrderSerializer

    def creaet(self, request,*args, **kwargs):
        user =  request.user
        cart_items = CartItem. objects.fillter(user = user)
        if not cart_items.exists():
            return Response({"detail": "Cart is empty."}, status=400)
        
        shipping = Shipping.objects.filter(user=user).last()
        if not shipping:
            return Response({"details":"Shiping info missing"}, status=400)
        
        # create order 
        order = Order.objects.create(
            user  =  user,
            shipping_address = str(shipping)
        )

        for item in cart_items:
            OrderItem.objects.create(
                order =  order,
                product =  item.product,
                quantity = item.quantity,
                price_at_item = item.product.price
            )
        cart_items.delete() #clear cart afater order place
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
