from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import WishlistItem
from .serializers import WishlistItemSerializer
from b2c.products.models import Products
from django.shortcuts import get_object_or_404

class WishlistListCreateView(generics.ListCreateAPIView):
    """
    GET: List all wishlist items for the logged-in user
    POST: Add a product to wishlist
    """
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # List wishlist items of the logged-in user
        return WishlistItem.objects.filter(user=self.request.user).select_related('product').order_by('-created_at')

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Products, id=product_id)

        # Check if already in wishlist
        wishlist_item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            return Response(
                {"detail": "Product is already in your wishlist."},
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(wishlist_item)
        return Response(
            {"message": "Product added to wishlist successfully.", "wishlist_item": serializer.data},
            status=status.HTTP_201_CREATED
        )


class WishlistRemoveView(generics.DestroyAPIView):
    """
    DELETE: Remove a product from wishlist
    """
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "item_id"

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        item_id = kwargs.get(self.lookup_url_kwarg)
        try:
            wishlist_item = self.get_queryset().get(id=item_id)
            wishlist_item.delete()
            return Response({"message": "Product removed from wishlist successfully."}, status=status.HTTP_200_OK)
        except WishlistItem.DoesNotExist:
            return Response({"error": "Wishlist item not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
