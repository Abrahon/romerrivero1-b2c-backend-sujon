# b2c/shipping/views.py

from rest_framework import generics, permissions
from .models import Shipping
from .serializers import ShippingSerializer

class ShippingListCreateView(generics.ListCreateAPIView):
    serializer_class = ShippingSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        return Shipping.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
