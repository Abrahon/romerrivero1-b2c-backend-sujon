from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from .models import Review
from .serializers import ReviewSerializer
from b2c.products.models import Products  # Make sure this import is correct based on your app structure
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

class ReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]  # Change to IsAuthenticatedOrReadOnly for better security

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Review.objects.filter(product_id=product_id).order_by('-created_at')

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Products, pk=product_id)
        serializer.save(user=self.request.user, product=product)


class ReviewDeleteAPIView(generics.DestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]  # Change to IsAuthenticated if needed

    def get_object(self):
        review = super().get_object()
        if review.user != self.request.user:
            raise PermissionDenied("You can only delete your own review.")
        return review
