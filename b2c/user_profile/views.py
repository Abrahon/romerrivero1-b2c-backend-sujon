from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from .models import UserProfile
from .serializers import UserProfileSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers


from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from .models import UserProfile
from .serializers import UserProfileSerializer
import re

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/profile/       -> retrieve current user's profile (auto-create if none)
    PUT  /api/profile/       -> replace profile fields
    PATCH /api/profile/      -> partial update (recommended for image uploads)
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        try:
            profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            return profile
        except Exception as e:
            raise serializers.ValidationError({"detail": f"Error retrieving profile: {str(e)}"})

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', True)  
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)

            # Manual field validation
            data = request.data
            errors = {}

            # Example: validate phone number (digits only, length 10-15)
            phone = data.get('phone')
            if phone:
                if not re.match(r'^\d{10,15}$', str(phone)):
                    errors['phone'] = "Phone number must contain 10-15 digits only."

            # Example: validate age (if provided)
            age = data.get('age')
            if age:
                try:
                    age_int = int(age)
                    if age_int < 0 or age_int > 120:
                        errors['age'] = "Age must be between 0 and 120."
                except ValueError:
                    errors['age'] = "Age must be a valid number."

            # Example: validate username (if provided)
            username = data.get('username')
            if username:
                if len(username) < 3:
                    errors['username'] = "Username must be at least 3 characters long."

            if errors:
                return Response({"success": False, "errors": errors}, status=status.HTTP_400_BAD_REQUEST)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "success": True,
                "message": "Profile updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except serializers.ValidationError as ve:
            return Response({"success": False, "errors": ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "message": f"Error updating profile: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# TODO: USER PROFILE DELETE API

class AdminUserProfileListView(generics.ListAPIView):
    """
    For admin: list all profiles
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        try:
            return UserProfile.objects.all().order_by('-updated_at')
        except Exception as e:
            return Response({"detail": f"Error fetching profiles: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
          