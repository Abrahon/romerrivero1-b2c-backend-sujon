from rest_framework import generics, permissions
from .models import CartItem
from .serializers import CartItemSerializer


class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        cart_item,created = CartItem.objects.get_or_create(
            user = user,
            product = product,
            defaults={'quantity', quantity}

        )
        # serializer.save(user=self.request.user)
        if not created:
            new_quantity = cart_item.quantity+quantity
            if product.stock<new_quantity:
                raise serializers.ValidationError(f"Only {product.stock} items available")
            cart_item = quantity = new_quantity
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
