# b2b/customers/views.py
from rest_framework import generics
from .models import Customer
from .serializers import CustomerSerializer
from rest_framework.permissions import IsAdminUser

class AdminCustomerCreateView(generics.CreateAPIView):
    """
    POST /api/customers/ -> Admin manually add a new customer.
    """
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]  # Ensure only admins can add customer data

    def perform_create(self, serializer):
        serializer.save()

class AdminCustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET, PUT, DELETE /api/customers/<id>/ -> Admin can view, update or delete customer details.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]  # Ensure only admins can update or delete