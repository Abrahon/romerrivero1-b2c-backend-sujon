from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import ShippingSerializer
from .models import Shipping

# Create your views here.

class ShippingListCreateView(generics.ListCreateAPIView):
    serializer_class = ShippingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Shipping.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    

