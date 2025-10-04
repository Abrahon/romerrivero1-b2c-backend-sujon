
from rest_framework import generics, permissions
from .models import Shipping
from .serializers import ShippingSerializer
from rest_framework.exceptions import ValidationError

class ShippingListCreateView(generics.ListCreateAPIView):
    serializer_class = ShippingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Shipping.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        order = serializer.validated_data.get('order')
        # prevent duplicate shipping for same order
        if order and Shipping.objects.filter(user=user, order=order).exists():
            raise ValidationError({"detail": "Shipping info for this order already exists."})
        serializer.save(user=user)

class ShippingRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShippingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    lookup_field = 'id'

    def get_queryset(self):
        return Shipping.objects.filter(user=self.request.user)
