from rest_framework import generics, permissions
from .models import CompanyDetails, Notification
from .serializers import CompanyDetailsSerializer, NotificationSerializer,ChangePasswordSerializer,EmailSecuritySerializer
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
# from .models import AdminProfile
from rest_framework.permissions import IsAdminUser
from rest_framework import generics, permissions
from .models import EmailSecurity
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AdminSujonProfile
from .serializers import AdminProfileSerializer
from django.contrib.auth import update_session_auth_hash
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
from rest_framework import generics, permissions, status, serializers  
from rest_framework.exceptions import PermissionDenied


# Admin Profile Views
class AdminProfileListCreateAPIView(generics.ListCreateAPIView):
    queryset = AdminSujonProfile.objects.all()
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)
    def perform_create(self, serializer):
        # Check if the user already has an AdminProfile
        user = self.request.user
        if AdminSujonProfile.objects.filter(user=user).exists():
            raise ValidationError("This user already has an AdminProfile.")
        
        # If no profile exists, save the new profile
        serializer.save(user=user)

class AdminProfileRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)
    http_method_names = ["get", "patch", "delete", "put"]

    def get_object(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only admins can access this profile.")
        try:
            return AdminSujonProfile.objects.get(user=self.request.user)
        except AdminSujonProfile.DoesNotExist:
            raise serializers.ValidationError({"error": "Admin profile does not exist."})

# Company Details Views

class CompanyDetailsListCreateAPIView(generics.ListCreateAPIView):
    queryset = CompanyDetails.objects.all()
    serializer_class = CompanyDetailsSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})


class CompanyDetailsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyDetails.objects.all()
    serializer_class = CompanyDetailsSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get', 'patch', 'delete']

    def perform_update(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})


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
