from django.shortcuts import render
# Create your views here.
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from accounts.permissions import IsAdminUser
from .models import Inquiry
from .serializers import InquirySerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from .serializers import AdminNotificationSerializer
from .models import AdminNotification

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


# class AdminNotificationListView(generics.ListAPIView):
#     """
#     GET /api/admin/notifications/ -> List all notifications for the logged-in admin
#     """
#     serializer_class = AdminNotificationSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         if not self.request.user.is_staff:
#             raise PermissionDenied("Only admins can view notifications.")
#         # Use the correct related_name for inquiries admin notifications
#         return self.request.user.inquiries_admin_notifications.order_by('-created_at')

    

# class MarkNotificationReadView(generics.UpdateAPIView):
#     """
#     PATCH /api/admin/notifications/<pk>/read/
#     Marks a specific notification as read for the admin.
#     """
#     queryset = AdminNotification.objects.all()
#     serializer_class = AdminNotificationSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_object(self):
#         obj = super().get_object()
#         if not self.request.user.is_staff:
#             raise PermissionDenied("Only admins can mark notifications as read.")
#         if obj.user != self.request.user:
#             raise PermissionDenied("You cannot mark other admin's notifications.")
#         return obj

#     def patch(self, request, *args, **kwargs):
#         notification = self.get_object()
#         notification.is_read = True
#         notification.save()
#         serializer = self.get_serializer(notification)
#         return Response(serializer.data, status=status.HTTP_200_OK)



class AdminNotificationListView(generics.ListAPIView):
    serializer_class = AdminNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can view notifications.")
        # use the related_name
        return self.request.user.inquiries_admin_notifications.order_by('-created_at')


class MarkNotificationReadView(generics.UpdateAPIView):
    serializer_class = AdminNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = AdminNotification.objects.all()
    
    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Only admins can mark notifications.")
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
