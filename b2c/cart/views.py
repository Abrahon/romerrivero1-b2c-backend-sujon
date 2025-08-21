from rest_framework import generics, permissions, serializers
from .models import CartItem
from .serializers import CartItemSerializer
from b2c.products.models import Products

class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]  # Require login

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            new_quantity = cart_item.quantity + quantity
            if product.stock < new_quantity:
                raise serializers.ValidationError(f"Only {product.stock} items available.")
            cart_item.quantity = new_quantity
            cart_item.save()


class CartItemUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        product = serializer.validated_data.get('product', serializer.instance.product)
        quantity = serializer.validated_data.get('quantity', serializer.instance.quantity)

        if product.stock < quantity:
            raise serializers.ValidationError(f"Only {product.stock} items available.")
        
        serializer.save()
    
