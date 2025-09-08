from django.contrib.auth import update_session_auth_hash
from rest_framework import generics, permissions, status, serializers
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import (
    CompanyDetails,
    Notification,
    EmailSecurity,
    AdminProfile,
)
from .serializers import (
    CompanyDetailsSerializer,
    NotificationSerializer,
    ChangePasswordSerializer,
    EmailSecuritySerializer,
    AdminProfileSerializer,
)


# ---------------------- Admin Profile Views ---------------------- #
class AdminProfileListCreateAPIView(generics.ListCreateAPIView):
    queryset = AdminProfile.objects.all()
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        """Ensure one AdminProfile per user"""
        user = self.request.user
        if AdminProfile.objects.filter(user=user).exists():
            raise ValidationError("This user already has an AdminProfile.")
        serializer.save(user=user)


class AdminProfileRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)
    http_method_names = ["get", "patch", "delete", "put"]

    def get_object(self):
        """Ensure only superusers can access their profile"""
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only admins can access this profile.")
        try:
            return AdminProfile.objects.get(user=self.request.user)
        except AdminProfile.DoesNotExist:
            raise serializers.ValidationError({"error": "Admin profile does not exist."})


# ---------------------- Company Details Views ---------------------- #
class CompanyDetailsListCreateAPIView(generics.ListCreateAPIView):
    queryset = CompanyDetails.objects.all()
    serializer_class = CompanyDetailsSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        """Handle errors gracefully on create"""
        try:
            serializer.save()
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})


class CompanyDetailsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyDetails.objects.all()
    serializer_class = CompanyDetailsSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ["get", "patch", "delete"]

    def perform_update(self, serializer):
        """Handle errors gracefully on update"""
        try:
            serializer.save()
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})


# ---------------------- Notifications ---------------------- #
class AdminNotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        """Return notifications for the logged-in admin"""
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")


# ---------------------- Email Security ---------------------- #
class EmailSecurityDetailUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = EmailSecuritySerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        """Ensure each user has one EmailSecurity object"""
        obj, _ = EmailSecurity.objects.get_or_create(user=self.request.user)
        return obj


# ---------------------- Change Password ---------------------- #
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request):
        return self._change_password(request)

    def patch(self, request):
        return self._change_password(request)

    def _change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["current_password"]):
            return Response({"current_password": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        update_session_auth_hash(request, user)  # keep user logged in
        return Response({"detail": "Password updated successfully"}, status=status.HTTP_200_OK)
