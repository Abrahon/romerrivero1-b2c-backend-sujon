from django.contrib.auth import update_session_auth_hash
from rest_framework import generics, permissions, status, serializers
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import CompanyDetails, EmailSecurity, AdminProfile
from .serializers import (
    CompanyDetailsSerializer,
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
        """Allow only one profile per admin user. If deleted, can recreate."""
        user = self.request.user

        if AdminProfile.objects.filter(user=user).exists():
            raise ValidationError({"error": "This user already has an AdminProfile."})

        # Use user first_name/last_name only if provided; allow client to override
        first_name = self.request.data.get("first_name") or user.first_name or ""
        last_name = self.request.data.get("last_name") or user.last_name or ""

        serializer.save(
            user=user,
            first_name=first_name,
            last_name=last_name,
        )



class AdminProfileRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)
    http_method_names = ["get", "patch", "delete", "put"]

    def get_object(self):
        try:
            return AdminProfile.objects.get(user=self.request.user)
        except AdminProfile.DoesNotExist:
            raise ValidationError({"error": "Admin profile does not exist."})

    def destroy(self, request, *args, **kwargs):
        print("hi")
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Admin profile deleted successfully"}, status=status.HTTP_200_OK)


# ---------------------- Company Details Views ---------------------- #
class CompanyDetailsListCreateAPIView(generics.ListCreateAPIView):
    queryset = CompanyDetails.objects.all()
    serializer_class = CompanyDetailsSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        """Ensure only one company profile exists system-wide."""
        if CompanyDetails.objects.exists():
            raise ValidationError({"error": "A company profile already exists. Delete it before creating a new one."})

        serializer.save()

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class CompanyDetailsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyDetails.objects.all()
    serializer_class = CompanyDetailsSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ["get", "patch", "delete"]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Company profile deleted successfully"}, status=status.HTTP_200_OK)




# ---------------------- Email Security ---------------------- #
class EmailSecurityDetailUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = EmailSecuritySerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        obj, created = EmailSecurity.objects.get_or_create(user=self.request.user)
        return obj

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            response.data = {"message": "Email security updated successfully", "data": response.data}
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ---------------------- Change Password ---------------------- #
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            instance=self.get_object(),
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        update_session_auth_hash(request, serializer.instance)
        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
