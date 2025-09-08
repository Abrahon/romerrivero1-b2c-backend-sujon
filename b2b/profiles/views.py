from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.contrib.auth import update_session_auth_hash

from .models import AdminSujonProfile, CompanyDetails, Notification, EmailSecurity
from .serializers import (
    AdminProfileSerializer,
    CompanyDetailsSerializer,
    NotificationSerializer,
    ChangePasswordSerializer,
    EmailSecuritySerializer,
)




# Admin Profile Views
class AdminProfileListCreateAPIView(generics.ListCreateAPIView):
    queryset = AdminSujonProfile.objects.all()
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAdminUser]  
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        user = self.request.user

        # Check if the current admin user already has a profile
        if AdminSujonProfile.objects.filter(user=user).exists():
            print("email", user)
            raise ValidationError("This admin user already has an AdminProfile.")

        # Save the new profile for the current admin user
        serializer.save(user=user)




class AdminProfileRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AdminSujonProfile.objects.all()
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "pk"

    def get_object(self):
        try:
            return self.request.user.adminsujonprofile
        except AdminSujonProfile.DoesNotExist:
            raise PermissionDenied("Profile does not exist for this admin.")

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        profile = self.get_object()
        profile.delete()
        return Response({"detail": "Profile deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# Company Details Views
class CompanyDetailsListCreateAPIView(generics.ListCreateAPIView):
    queryset = CompanyDetails.objects.all()
    serializer_class = CompanyDetailsSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAdminUser]  


class CompanyDetailsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyDetails.objects.all()
    serializer_class = CompanyDetailsSerializer
    permission_classes = [permissions.IsAdminUser]


# Notifications (Admin)
class AdminNotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")


class EmailSecurityDetailUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = EmailSecuritySerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        # Ensure the current logged-in user always manages their own EmailSecurity
        obj, created = EmailSecurity.objects.get_or_create(user=self.request.user)
        return obj


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request):
        return self._change_password(request)

    def patch(self, request):
        return self._change_password(request)

    def _change_password(self, request):
        print(request.data)
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["current_password"]):
            return Response({"current_password": "Incorrect password"}, status=400)

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        update_session_auth_hash(request, user)
        return Response({"detail": "Password updated successfully"}, status=200)
