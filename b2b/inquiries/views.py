from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Inquiry, AdminNotification
from .serializers import InquirySerializer, AdminNotificationSerializer
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from b2b.accounts_b.models import B2BUser


class InquiryListCreateView(generics.ListCreateAPIView):
    serializer_class = InquirySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if isinstance(self.request.user, B2BUser):
            # B2B users see only their inquiries
            return Inquiry.objects.filter(user=self.request.user)
        # Admins can see all inquiries
        if self.request.user.is_staff:
            return Inquiry.objects.all()
        # Otherwise, empty queryset
        return Inquiry.objects.none()

    def perform_create(self, serializer):
        if not isinstance(self.request.user, B2BUser):
            raise PermissionDenied("Only B2B users can create inquiries.")
        serializer.save(user=self.request.user)




class InquiryUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer
    permission_classes = [IsAdminUser]

    def get_object(self):
        obj = super().get_object()
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can manage inquiries.")
        return obj

# -------------------------------
# Admin Notification Views
# -------------------------------
class AdminNotificationListView(generics.ListAPIView):
    serializer_class = AdminNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can view notifications.")
        return self.request.user.inquiries_admin_notifications.all()


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
        return Response(serializer.data, status=status.HTTP_200_OK)
