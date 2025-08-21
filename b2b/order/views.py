from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Order
from .serializers import OrderSerializer
from django.shortcuts import get_object_or_404
from b2b.inquiries.models import Inquiry

# User can create an order from an inquiry
class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Ensure that the order is linked to an inquiry
        inquiry = get_object_or_404(Inquiry, id=self.request.data.get('inquiry'))  # Get inquiry by ID
        serializer.save(user=self.request.user, inquiry=inquiry)

# Admin can read, update, and delete orders
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admin can access

    def get_queryset(self):
        # Admin can see all orders
        return Order.objects.all()

    def perform_update(self, serializer):
        # Add any custom logic for updating orders if necessary
        serializer.save()

    def perform_destroy(self, instance):
        # Admin can delete the order
        instance.delete()

# Admin can list all orders
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        # Admin can see all orders
        return Order.objects.all()
