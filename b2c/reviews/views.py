from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Review
from .serializers import ReviewSerializer
from b2c.products.models import Products 
from django.db.models import Avg


# List and Create Reviews
class ReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None
    

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Review.objects.filter(product_id=product_id).order_by('-created_at')

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Products, pk=product_id)

        # ✅ Allow multiple reviews from the same user
        review = serializer.save(user=self.request.user, product=product)

        # ✅ Update product’s average rating after saving review
        avg_rating = Review.objects.filter(product=product).aggregate(avg=Avg("rating"))["avg"] or 0
        product.avg_rating = round(avg_rating, 1)  # keep one decimal place
        product.save(update_fields=["avg_rating"])


# Update Review
class ReviewUpdateAPIView(generics.UpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]  
    pagination_class = None

    def get_object(self):
        review = super().get_object()
        if review.user != self.request.user:  
            raise PermissionDenied("You can only update your own review.")
        return review

    def patch(self, request, *args, **kwargs):
        review = self.get_object()
        serializer = self.get_serializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        avg_rating = Review.objects.filter(product=review.product).aggregate(avg=Avg("rating"))["avg"] or 0
        review.product.avg_rating = round(avg_rating, 1)
        review.product.save(update_fields=["avg_rating"])

        return Response({
            "status": "Review updated successfully.",
            "review": serializer.data
        }, status=status.HTTP_200_OK)


# Delete Review (Owner or Admin)
class ReviewDeleteAPIView(generics.DestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated] 
    pagination_class = None 

    def get_object(self):
        review = super().get_object()
        user = self.request.user
        if review.user != user and not user.is_staff:
            raise PermissionDenied("You can only delete your own review or you must be an admin.")
        return review

    def delete(self, request, *args, **kwargs):
        review = self.get_object()
        product = review.product
        review.delete()

        # ✅ Recalculate average rating after deletion
        avg_rating = Review.objects.filter(product=product).aggregate(avg=Avg("rating"))["avg"] or 0
        product.avg_rating = round(avg_rating, 1)
        product.save(update_fields=["avg_rating"])

        return Response({"status": "Review deleted successfully."}, status=status.HTTP_200_OK)



class TopReviewsListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  

    def get_queryset(self):
        
        return Review.objects.filter(rating__isnull=False).order_by('-rating', '-created_at')[:8]
    


    




