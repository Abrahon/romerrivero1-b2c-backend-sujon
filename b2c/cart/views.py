
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from .models import CartItem
from .serializers import CartItemSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q

from rest_framework import generics, permissions
from .models import CartItem
from .serializers import CartItemSerializer
from rest_framework import serializers




class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        # Step 1: Get all cart items for the user
        cart_items = CartItem.objects.filter(user=self.request.user)

        # Step 2: Remove items where product is out of stock or inactive
        out_of_stock_items = cart_items.filter(
            Q(product__available_stock__lte=0) | Q(product__status="inactive")
        )

        if out_of_stock_items.exists():
            out_of_stock_items.delete()

        # Step 3: Return updated queryset
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Handles add-to-cart logic.
        If product is already in cart, update quantity.
        If product is out of stock, prevent adding.
        """
        product = serializer.validated_data.get("product")

        # Check stock before adding
        if product.available_stock <= 0 or product.status == "inactive":
            raise serializers.ValidationError({"error": "This product is out of stock."})

        # Proceed normally
        serializer.save(user=self.request.user)



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
