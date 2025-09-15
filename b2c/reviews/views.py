from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Review
from .serializers import ReviewSerializer
from b2c.products.models import Products  # Make sure import matches your project structure



# List and Create Reviews

class ReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Authenticated users can create

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Review.objects.filter(product_id=product_id).order_by('-created_at')

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Products, pk=product_id)
        
        # Optional: prevent duplicate reviews by the same user for the same product
        if Review.objects.filter(user=self.request.user, product=product).exists():
            raise ValidationError("You have already reviewed this product.")

        serializer.save(user=self.request.user, product=product)


class ReviewUpdateAPIView(generics.UpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]  

    def get_object(self):
        review = super().get_object()
        user = self.request.user
        if review.user != user:  
            raise PermissionDenied("You can only update your own review.")
        return review

    def patch(self, request, *args, **kwargs):
        review = self.get_object()
        serializer = self.get_serializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "status": "Review updated successfully.",
            "review": serializer.data
        }, status=status.HTTP_200_OK)




# Delete Review (Owner or Admin)

class ReviewDeleteAPIView(generics.DestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]  

    def get_object(self):
        review = super().get_object()
        user = self.request.user

        if review.user != user and not user.is_staff:
            raise PermissionDenied("You can only delete your own review or you must be an admin.")
        return review

    def delete(self, request, *args, **kwargs):
        review = self.get_object()
        review.delete()
        return Response({"status": "Review deleted successfully."}, status=status.HTTP_200_OK)
