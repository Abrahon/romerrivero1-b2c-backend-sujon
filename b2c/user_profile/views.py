from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from .models import UserProfile
from .serializers import UserProfileSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers



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
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": f"Error updating profile: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


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
