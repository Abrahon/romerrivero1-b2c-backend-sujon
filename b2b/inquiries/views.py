from django.shortcuts import render
# Create your views here.
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from accounts.permissions import IsAdminUser
from .models import Inquiry
from .serializers import InquirySerializer
from rest_framework.permissions import IsAuthenticated,AllowAny

class InquiryListCreateView(generics.ListCreateAPIView):
    """
    GET /api/inquiries/ -> List all inquiries for admin
    POST /api/inquiries/ -> Create a new inquiry (typically for user)
    """
    serializer_class = InquirySerializer
    permission_classes = [IsAuthenticated]  

    def get_queryset(self):
        # Only fetch inquiries for the logged-in user (admin can see all inquiries)
        if self.request.user.is_staff:
            return Inquiry.objects.all()  
        return Inquiry.objects.filter(user=self.request.user)  # User can see only their inquiries

    def perform_create(self, serializer):
        # Automatically associate the logged-in user with the inquiry
        serializer.save(user=self.request.user)


# class InquiryUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
#     """
#     PUT /api/inquiries/<id>/ -> Update an inquiry (for admin)
#     DELETE /api/inquiries/<id>/ -> Delete an inquiry (for admin)
#     """
#     serializer_class = InquirySerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Inquiry.objects.all()  # Admin can update or delete any inquiry
# class IsAdminUser(permissions.BasePermission):
#     """
#     Custom permission to allow only admin users to access.
#     """

#     def has_permission(self, request, view):
#         return request.user and request.user.is_staff 

class InquiryUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/inquiries/<id>/    -> Retrieve an inquiry (only admin)
    PUT    /api/inquiries/<id>/    -> Update an inquiry (only admin)
    DELETE /api/inquiries/<id>/    -> Delete an inquiry (only admin)
    """

    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer
    permission_classes = [IsAdminUser]

    def get_object(self):
        """
        Allow only admins to access inquiries.
        """
        obj = super().get_object()
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can view or manage inquiries.")
        return obj