
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from .models import CartItem
from .serializers import CartItemSerializer


from rest_framework.parsers import MultiPartParser, FormParser

from rest_framework import generics, permissions
from .models import CartItem
from .serializers import CartItemSerializer

class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Just call serializer.save() - create() method handles get_or_create and quantity update
        serializer.save()




class CartItemUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def get_object(self):
        try:
            return super().get_object()
        except Exception:
            raise NotFound({"detail": "Cart item not found."})

    def perform_update(self, serializer):
        quantity = serializer.validated_data.get("quantity", serializer.instance.quantity)
        product = serializer.instance.product

        if quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be greater than zero."})
        if product.available_stock < quantity:
            raise ValidationError({"quantity": f"Only {product.available_stock} items available in stock."})

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Item removed from cart successfully."}, status=status.HTTP_204_NO_CONTENT)
