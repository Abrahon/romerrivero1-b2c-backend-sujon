from rest_framework import generics, permissions, serializers
from .models import CartItem
from .serializers import CartItemSerializer
from b2c.products.models import Products
from rest_framework.exceptions import ValidationError
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from .models import CartItem
from .serializers import CartItemSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import CartItem
from .serializers import CartItemSerializer


class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None 

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        user = self.request.user

        # Check duplicate
        if CartItem.objects.filter(user=user, product=product).exists():
            raise ValidationError({
                "detail": "This product is already in your cart. You can update the quantity instead."
            })

        serializer.save(user=user)


class CartItemUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'  
    pagination_class = None

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        quantity = serializer.validated_data.get('quantity', serializer.instance.quantity)
        print("quantity", quantity)
        product = serializer.instance.product

        if quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be greater than zero."})
        if product.available_stock < quantity:
            raise ValidationError({"quantity": f"Only {product.available_stock} items available in stock."})

        serializer.save()






# class CartItemUpdateByProductView(generics.GenericAPIView):
#     serializer_class = CartItemSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def patch(self, request, *args, **kwargs):
#         product_id = request.data.get("product_id")
#         if not product_id:
#             return Response({"product_id": "This field is required."}, status=400)

#         try:
#             cart_item = CartItem.objects.get(user=request.user, product_id=product_id)
#         except CartItem.DoesNotExist:
#             return Response({"detail": "Cart item not found."}, status=404)

#         serializer = self.get_serializer(cart_item, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)


