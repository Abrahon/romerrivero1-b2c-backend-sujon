# from django.contrib.auth import update_session_auth_hash
# from rest_framework import generics, permissions, status, serializers
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.response import Response
# from rest_framework.exceptions import ValidationError, PermissionDenied

# from .models import CompanyDetails, EmailSecurity, AdminProfile
# from .serializers import (
#     CompanyDetailsSerializer,
#     ChangePasswordSerializer,
#     EmailSecuritySerializer,
#     AdminProfileSerializer,
# )

# # ---------------------- Admin Profile Views ---------------------- #
# class AdminProfileListCreateAPIView(generics.ListCreateAPIView):
#     queryset = AdminProfile.objects.all()
#     serializer_class = AdminProfileSerializer
#     permission_classes = [permissions.IsAdminUser]
#     parser_classes = (MultiPartParser, FormParser)

#     def perform_create(self, serializer):
#         """Allow only one profile per admin user. If deleted, can recreate."""
#         user = self.request.user

#         if AdminProfile.objects.filter(user=user).exists():
#             raise ValidationError({"error": "This user already has an AdminProfile."})

#         # Use user first_name/last_name only if provided; allow client to override
#         first_name = self.request.data.get("first_name") or user.first_name or ""
#         last_name = self.request.data.get("last_name") or user.last_name or ""

#         serializer.save(
#             user=user,
#             first_name=first_name,
#             last_name=last_name,
#         )



# class AdminProfileRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = AdminProfileSerializer
#     permission_classes = [permissions.IsAdminUser]
#     parser_classes = (MultiPartParser, FormParser)
#     http_method_names = ["get", "patch", "delete", "put"]

#     def get_object(self):
#         try:
#             return AdminProfile.objects.get(user=self.request.user)
#         except AdminProfile.DoesNotExist:
#             raise ValidationError({"error": "Admin profile does not exist."})

#     def destroy(self, request, *args, **kwargs):
#         print("hi")
#         instance = self.get_object()
#         instance.delete()
#         return Response({"message": "Admin profile deleted successfully"}, status=status.HTTP_200_OK)


# # ---------------------- Company Details Views ---------------------- #
# class CompanyDetailsListCreateAPIView(generics.ListCreateAPIView):
#     queryset = CompanyDetails.objects.all()
#     serializer_class = CompanyDetailsSerializer
#     parser_classes = (MultiPartParser, FormParser)
#     permission_classes = [permissions.IsAdminUser]

#     def perform_create(self, serializer):
#         """Ensure only one company profile exists system-wide."""
#         if CompanyDetails.objects.exists():
#             raise ValidationError({"error": "A company profile already exists. Delete it before creating a new one."})

#         serializer.save()

#     def create(self, request, *args, **kwargs):
#         try:
#             return super().create(request, *args, **kwargs)
#         except ValidationError as e:
#             return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


# class CompanyDetailsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = CompanyDetails.objects.all()
#     serializer_class = CompanyDetailsSerializer
#     parser_classes = (MultiPartParser, FormParser)
#     permission_classes = [permissions.IsAdminUser]
#     http_method_names = ["get", "patch", "delete"]

#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         instance.delete()
#         return Response({"message": "Company profile deleted successfully"}, status=status.HTTP_200_OK)




# # ---------------------- Email Security ---------------------- #
# class EmailSecurityDetailUpdateView(generics.RetrieveUpdateAPIView):
#     serializer_class = EmailSecuritySerializer
#     permission_classes = [permissions.IsAdminUser]

#     def get_object(self):
#         obj, created = EmailSecurity.objects.get_or_create(user=self.request.user)
#         return obj

#     def update(self, request, *args, **kwargs):
#         try:
#             response = super().update(request, *args, **kwargs)
#             response.data = {"message": "Email security updated successfully", "data": response.data}
#             return response
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# # ---------------------- Change Password ---------------------- #
# class ChangePasswordView(generics.UpdateAPIView):
#     serializer_class = ChangePasswordSerializer
#     permission_classes = [permissions.IsAdminUser]

#     def get_object(self):
#         return self.request.user

#     def update(self, request, *args, **kwargs):
#         serializer = self.get_serializer(
#             instance=self.get_object(),
#             data=request.data,
#             context={'request': request}
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         update_session_auth_hash(request, serializer.instance)
#         return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)

from django.contrib.auth import update_session_auth_hash
from rest_framework import generics, permissions, status, serializers
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import CompanyDetails, Notification, EmailSecurity, AdminProfile
from .serializers import (
    CompanyDetailsSerializer,
    NotificationSerializer,
    ChangePasswordSerializer,
    EmailSecuritySerializer,
    AdminProfileSerializer,
)

# ---------------------- Admin Profile Views ---------------------- #
# views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import AdminProfile
from .serializers import AdminProfileSerializer
from rest_framework import serializers

class AdminProfileView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET  /api/admin-profile/    -> retrieve current admin's profile (auto-create if missing)
    PATCH /api/admin-profile/   -> partial update (recommended for image uploads)
    PUT  /api/admin-profile/    -> full update
    DELETE /api/admin-profile/ -> delete admin profile from DB
    """
    serializer_class = AdminProfileSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None 

    def get_object(self):
        # Auto-create profile if it doesn't exist
        profile, created = AdminProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                "first_name": getattr(self.request.user, "first_name", ""),
                "last_name": getattr(self.request.user, "last_name", ""),
            }
        )
        return profile

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # default to partial update
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Profile updated successfully", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "Profile deleted successfully"},
            status=status.HTTP_200_OK
        )


# ---------------------- Company Details Views ---------------------- #



class CompanyDetailsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/company-profile/    -> retrieve current admin's company profile (auto-create if missing)
    PATCH  /api/company-profile/    -> partial update (recommended for image uploads)
    PUT    /api/company-profile/    -> full update
    DELETE /api/company-profile/    -> delete company profile
    """
    serializer_class = CompanyDetailsSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ["get", "patch", "put", "delete"]
    pagination_class = None

    def get_object(self):
        # Auto-create company profile if it doesn't exist
        profile, created = CompanyDetails.objects.get_or_create(
            user=self.request.user,
            defaults={
                "company_name": "",
                "industry_type": "",
                "company_email": getattr(self.request.user, "email", ""),
                "company_phone": "",
                "company_address": "",
            }
        )
        return profile

    def update(self, request, *args, **kwargs):
        # Determine if partial update
        partial = request.method.lower() == "patch"
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Company profile updated successfully", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "Company profile deleted successfully"},
            status=status.HTTP_200_OK
        )



# ---------------------- Notifications ---------------------- #
class AdminNotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user).order_by("-created_at")
        if not qs.exists():
            raise serializers.ValidationError({"message": "No notifications available."})
        return qs


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
