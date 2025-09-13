from rest_framework import generics, permissions, serializers
from .models import CartItem
from .serializers import CartItemSerializer
from b2c.products.models import Products
from rest_framework.exceptions import ValidationError



class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

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

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        product = serializer.instance.product
        quantity = serializer.validated_data.get('quantity', serializer.instance.quantity)

        if quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be greater than zero."})

        if product.available_stock < quantity:
            raise ValidationError({
                "quantity": f"Only {product.available_stock} items available in stock."
            })

        serializer.save()

    
