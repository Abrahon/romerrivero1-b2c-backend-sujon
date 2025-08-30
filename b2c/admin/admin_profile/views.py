from rest_framework import generics, permissions
from .models import AdminProfile, CompanyDetails, Notification
from .serializers import AdminProfileSerializer, CompanyDetailsSerializer, NotificationSerializer
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from .models import AdminProfile
from .serializers import EmailSecuritySerializer, ChangePasswordSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework import generics, permissions
from .models import EmailSecurity
# from .serializers import EmailSecuritySerializer
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import update_session_auth_hash
from .serializers import ChangePasswordSerializer


# Admin Profile Views
class AdminProfileListCreateAPIView(generics.ListCreateAPIView):
    queryset = AdminProfile.objects.all()
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAdminUser]  


class AdminProfileRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AdminProfile.objects.all()
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAdminUser]


# Company Details Views
class CompanyDetailsListCreateAPIView(generics.ListCreateAPIView):
    queryset = CompanyDetails.objects.all()
    serializer_class = CompanyDetailsSerializer
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
